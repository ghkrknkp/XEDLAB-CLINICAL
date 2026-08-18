"""Password hashing, JWT token management, and endpoint rate limiting using direct bcrypt."""
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List

import bcrypt
from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    # bcrypt standard hashing (truncating at 72 bytes per bcrypt spec)
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


class RateLimiter:
    """Sliding-window in-memory rate limiter per client/user key."""

    def __init__(self):
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, key: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        now = time.time()
        window_start = now - window_seconds

        # Prune older timestamps
        self._requests[key] = [ts for ts in self._requests[key] if ts > window_start]

        if len(self._requests[key]) >= max_requests:
            return False

        self._requests[key].append(now)
        return True


rate_limiter = RateLimiter()
