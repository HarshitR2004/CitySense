"""Celery tasks for async CitySense report processing."""

from __future__ import annotations

import logging

from celery.exceptions import Retry

from app.core.celery_app import celery_app
from app.core.logging_config import configure_logging
from app.models.queue_schema import AIProcessingStatus, ProcessingStage
from app.services.ai_processing_service import AIProcessingService

configure_logging()

logger = logging.getLogger(__name__)


def _is_transient_error(exc: Exception) -> bool:
    message = str(exc).lower()
    transient_markers = (
        "timeout",
        "tempor",
        "connection",
        "unavailable",
        "rate limit",
        "resource exhausted",
        "broken pipe",
        "reset by peer",
    )

    if isinstance(exc, ValueError):
        return False

    return any(marker in message for marker in transient_markers) or isinstance(exc, (ConnectionError, TimeoutError))


@celery_app.task(
    bind=True,
    name="citysense.process_report_ai",
    acks_late=True,
    reject_on_worker_lost=True,
    max_retries=3,
)
def process_report_ai(self, report_id: str) -> dict:
    """Process a report asynchronously and persist progress to Firestore."""

    service = AIProcessingService()

    try:
        logger.info("Starting async AI processing for report %s", report_id)
        result = service.process_report(report_id)
        logger.info("Completed async AI processing for report %s", report_id)
        return result

    except Retry:
        raise
    except Exception as exc:
        logger.warning(
            "AI task failed for report %s on attempt %s: %s",
            report_id,
            self.request.retries,
            exc,
        )

        if _is_transient_error(exc) and self.request.retries < self.max_retries:
            service.firestore_service.update_ai_processing_state(
                report_id,
                ai_status=AIProcessingStatus.PROCESSING,
                stage=ProcessingStage.RETRYING,
                progress=service.firestore_service.get_report_by_id(report_id).get("progress", 0),
                processing_error=str(exc),
            )
            raise self.retry(exc=exc, countdown=min(2 ** self.request.retries, 60))

        service.mark_failed(report_id, exc)
        raise
