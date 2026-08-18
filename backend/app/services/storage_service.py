"""Storage service abstraction for uploaded medical reports.

Provides LocalStorage for development/offline mode and S3-compatible object
storage for production environments.
"""
import os
import shutil
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO

from app.core.config import get_settings
from app.core.logging import log_event

settings = get_settings()


class StorageService(ABC):
    """Abstract interface for storing and retrieving report files."""

    @abstractmethod
    def save_file(self, file_bytes: bytes, filename: str) -> str:
        """Saves file bytes and returns the stored path or key."""
        pass

    @abstractmethod
    def read_file(self, stored_path: str) -> bytes:
        """Reads and returns file bytes."""
        pass

    @abstractmethod
    def delete_file(self, stored_path: str) -> bool:
        """Deletes the stored file."""
        pass

    @abstractmethod
    def generate_secure_url(self, stored_path: str, expires_in_seconds: int = 3600) -> Optional[str]:
        """Generates a temporary pre-signed access URL if supported."""
        pass


class LocalStorageService(StorageService):
    """Stores files on the local filesystem in a sandboxed upload directory."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or settings.upload_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _sanitize_path(self, filename: str) -> str:
        # Protect against path traversal (e.g., ../../etc/passwd)
        clean_name = os.path.basename(filename)
        dest_path = os.path.abspath(os.path.join(self.base_dir, clean_name))
        if not dest_path.startswith(self.base_dir):
            raise ValueError("Path traversal attempt detected.")
        return dest_path

    def save_file(self, file_bytes: bytes, filename: str) -> str:
        target_path = self._sanitize_path(filename)
        with open(target_path, "wb") as f:
            f.write(file_bytes)
        return target_path

    def read_file(self, stored_path: str) -> bytes:
        if not os.path.exists(stored_path):
            raise FileNotFoundError("Report file not found.")
        with open(stored_path, "rb") as f:
            return f.read()

    def delete_file(self, stored_path: str) -> bool:
        if os.path.exists(stored_path):
            try:
                os.remove(stored_path)
                return True
            except OSError:
                return False
        return False

    def generate_secure_url(self, stored_path: str, expires_in_seconds: int = 3600) -> Optional[str]:
        # Local files do not have public presigned URLs; served through authenticated endpoints
        return None


class S3StorageService(StorageService):
    """Production S3 / MinIO compatible storage."""

    def __init__(self):
        import boto3
        from botocore.config import Config

        session = boto3.session.Session()
        self.s3_client = session.client(
            "s3",
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url or None,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.s3_bucket

    def save_file(self, file_bytes: bytes, filename: str) -> str:
        key = f"reports/{os.path.basename(filename)}"
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_bytes,
            ServerSideEncryption="AES256",
        )
        return key

    def read_file(self, stored_path: str) -> bytes:
        response = self.s3_client.get_object(Bucket=self.bucket, Key=stored_path)
        return response["Body"].read()

    def delete_file(self, stored_path: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=stored_path)
            return True
        except Exception:
            return False

    def generate_secure_url(self, stored_path: str, expires_in_seconds: int = 3600) -> Optional[str]:
        try:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": stored_path},
                ExpiresIn=expires_in_seconds,
            )
        except Exception:
            return None


def get_storage_service() -> StorageService:
    """Factory returns configured storage provider."""
    if settings.storage_provider == "s3" and settings.s3_bucket and settings.s3_access_key:
        try:
            return S3StorageService()
        except Exception:
            # Fallback to local if S3 connection initialization fails
            return LocalStorageService()
    return LocalStorageService()
