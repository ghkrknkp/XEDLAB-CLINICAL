from fastapi import APIRouter
from app.database.database import engine
from app.core.config import get_settings
from app.schemas.response import HealthResponse, ReadyResponse

router = APIRouter(prefix="/api", tags=["health"])
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="healthy", version="1.0.0")


@router.get("/ready", response_model=ReadyResponse)
def readiness_check():
    db_status = "ok"
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
    except Exception:
        db_status = "error"

    redis_status = "ok"
    try:
        import redis
        r = redis.from_url(settings.redis_url, socket_timeout=1)
        r.ping()
    except Exception:
        redis_status = "unreachable (using in-process fallback)"

    storage_status = "ok"

    is_ready = db_status == "ok"
    return ReadyResponse(
        status="ready" if is_ready else "degraded",
        database=db_status,
        redis=redis_status,
        storage=storage_status,
    )
