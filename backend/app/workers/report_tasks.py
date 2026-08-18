"""Background task dispatcher and Celery task definition.

Supports both:
1. Production: Celery background worker queue over Redis
2. Local / Development Fallback: In-process asynchronous thread pool when Redis is offline
"""
import concurrent.futures
import logging
from app.workers.celery_app import celery_app
from app.services.report_pipeline import process_report_pipeline
from app.core.logging import log_event

logger = logging.getLogger("medreports")
_local_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

if celery_app is not None:
    @celery_app.task(name="tasks.process_report", bind=True, max_retries=2, default_retry_delay=10)
    def celery_process_report_task(self, report_id: str, job_id: str):
        """Celery background task."""
        try:
            process_report_pipeline(report_id, job_id)
        except Exception as exc:
            log_event("celery_task_retry", report_id=report_id, job_id=job_id, level=30)
            raise self.retry(exc=exc)
else:
    celery_process_report_task = None


def dispatch_report_processing(report_id: str, job_id: str):
    """Dispatches processing task to Celery or in-process background runner."""
    dispatched_celery = False
    if celery_process_report_task is not None:
        try:
            celery_process_report_task.delay(report_id, job_id)
            log_event("task_dispatched_celery", report_id=report_id, job_id=job_id)
            dispatched_celery = True
        except Exception:
            dispatched_celery = False

    if not dispatched_celery:
        # Fallback to local background thread execution
        _local_executor.submit(process_report_pipeline, report_id, job_id)
        log_event("task_dispatched_local_fallback", report_id=report_id, job_id=job_id)
