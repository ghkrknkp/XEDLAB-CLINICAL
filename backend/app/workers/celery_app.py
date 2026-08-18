"""Celery application configuration for background medical report processing."""
import os
import logging
from app.core.config import get_settings

logger = logging.getLogger("medreports")
settings = get_settings()

try:
    from celery import Celery

    celery_app = Celery(
        "medreports_worker",
        broker=settings.redis_url,
        backend=settings.redis_url,
        include=["app.workers.report_tasks"],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,  # 5 minutes maximum
        worker_prefetch_multiplier=1,
    )
except ImportError:
    logger.info("Celery not installed; background runner will use in-process thread pool.")
    celery_app = None
