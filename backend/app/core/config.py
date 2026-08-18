"""Application configuration loaded from environment variables (.env)."""
import os
from functools import lru_cache
from typing import List, Union

try:
    from pydantic import field_validator
    from pydantic_settings import BaseSettings, SettingsConfigDict
    _HAS_PYDANTIC_SETTINGS = True
except ImportError:
    _HAS_PYDANTIC_SETTINGS = False
    BaseSettings = object


if _HAS_PYDANTIC_SETTINGS:
    class Settings(BaseSettings):
        app_env: str = "development"
        app_name: str = "AI Medical Report Analyzer"
        port: int = 8000
        host: str = "0.0.0.0"

        # Security & Auth
        secret_key: str = "insecure-dev-secret-change-me-for-production-min32chars"
        jwt_algorithm: str = "HS256"
        access_token_expire_minutes: int = 120

        # Database & Redis
        database_url: str = "sqlite:///./medreports.db"
        redis_url: str = "redis://localhost:6379/0"

        # Storage
        storage_provider: str = "local"  # "local" | "s3"
        upload_dir: str = "./storage/uploads"
        max_file_size_mb: int = 10
        report_retention_days: int = 90

        # S3 Storage (Production)
        s3_bucket: str = ""
        s3_region: str = "us-east-1"
        s3_access_key: str = ""
        s3_secret_key: str = ""
        s3_endpoint_url: str = ""  # for MinIO or custom S3-compatible storage

        # LLM Providers (OpenAI / Gemini / Local fallback)
        llm_provider: str = "none"  # "openai" | "gemini" | "none"
        openai_api_key: str = ""
        openai_model: str = "gpt-4o-mini"
        gemini_api_key: str = ""
        gemini_model: str = "gemini-1.5-flash"

        # OCR
        tesseract_cmd: str = "tesseract"

        # CORS & Frontend
        frontend_url: str = "http://localhost:5173"
        allowed_origins: Union[str, List[str]] = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
        ]

        # Rate Limiting
        rate_limit_per_minute: int = 60
        qa_rate_limit_per_minute: int = 20

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
        )

        @field_validator("allowed_origins", mode="before")
        @classmethod
        def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
            if isinstance(v, str) and not v.startswith("["):
                return [i.strip() for i in v.split(",") if i.strip()]
            elif isinstance(v, list):
                return v
            return ["http://localhost:5173", "http://localhost:3000"]

        @property
        def max_file_size_bytes(self) -> int:
            return self.max_file_size_mb * 1024 * 1024

else:
    class Settings:
        def __init__(self):
            self.app_env = os.getenv("APP_ENV", "development")
            self.app_name = os.getenv("APP_NAME", "AI Medical Report Analyzer")
            self.port = int(os.getenv("PORT", "8000"))
            self.host = os.getenv("HOST", "0.0.0.0")

            self.secret_key = os.getenv("SECRET_KEY", "insecure-dev-secret-change-me-for-production-min32chars")
            self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
            self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

            self.database_url = os.getenv("DATABASE_URL", "sqlite:///./medreports.db")
            self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

            self.storage_provider = os.getenv("STORAGE_PROVIDER", "local")
            self.upload_dir = os.getenv("UPLOAD_DIR", "./storage/uploads")
            self.max_file_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
            self.report_retention_days = int(os.getenv("REPORT_RETENTION_DAYS", "90"))

            self.s3_bucket = os.getenv("S3_BUCKET", "")
            self.s3_region = os.getenv("S3_REGION", "us-east-1")
            self.s3_access_key = os.getenv("S3_ACCESS_KEY", "")
            self.s3_secret_key = os.getenv("S3_SECRET_KEY", "")
            self.s3_endpoint_url = os.getenv("S3_ENDPOINT_URL", "")

            self.llm_provider = os.getenv("LLM_PROVIDER", "none")
            self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
            self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
            self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

            self.tesseract_cmd = os.getenv("TESSERACT_CMD", "tesseract")

            self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
            origins_raw = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000")
            self.allowed_origins = [o.strip() for o in origins_raw.split(",") if o.strip()]

            self.rate_limit_per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
            self.qa_rate_limit_per_minute = int(os.getenv("QA_RATE_LIMIT_PER_MINUTE", "20"))

        @property
        def max_file_size_bytes(self) -> int:
            return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
