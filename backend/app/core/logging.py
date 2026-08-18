"""Privacy-preserving structured logging system.

MANDATE (Requirement #23, #35):
- Never log raw medical report content
- Never log OCR text
- Never log patient names or IDs
- Never log lab values or test names
- Never log API keys or secrets

Only log safe correlation identifiers:
- report_id
- job_id
- stage
- status
- duration
- safe error code
"""
import logging
import sys
from typing import Optional


class SafeMedicalLogFormatter(logging.Formatter):
    """Custom log formatter ensuring uniform format without sensitive data leakage."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, self.datefmt)
        return f"[{timestamp}] [{record.levelname}] {record.getMessage()}"


def setup_logger(name: str = "medreports", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if re-initialized
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(SafeMedicalLogFormatter(datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)

    logger.propagate = False
    return logger


logger = setup_logger()


def log_event(
    event: str,
    report_id: Optional[str] = None,
    job_id: Optional[str] = None,
    stage: Optional[str] = None,
    status: Optional[str] = None,
    duration_ms: Optional[float] = None,
    error_code: Optional[str] = None,
    level: int = logging.INFO,
):
    """Logs safe operational telemetry without exposing medical details."""
    parts = [f"event={event}"]
    if report_id:
        parts.append(f"report_id={report_id}")
    if job_id:
        parts.append(f"job_id={job_id}")
    if stage:
        parts.append(f"stage={stage}")
    if status:
        parts.append(f"status={status}")
    if duration_ms is not None:
        parts.append(f"duration_ms={duration_ms:.1f}")
    if error_code:
        parts.append(f"error_code={error_code}")

    msg = " ".join(parts)
    logger.log(level, msg)
