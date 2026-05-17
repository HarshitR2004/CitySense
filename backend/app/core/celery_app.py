from __future__ import annotations

import logging
import os

from celery import Celery

from app.core.logging_config import configure_logging

configure_logging()

logger = logging.getLogger(__name__)


def _broker_url() -> str:
    return os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")


def _backend_url() -> str:
    return os.getenv("CELERY_RESULT_BACKEND", _broker_url())


celery_app = Celery(
    "citysense",
    broker=_broker_url(),
    backend=_backend_url(),
    include=["app.tasks.report_tasks"],
)

celery_app.conf.update(
    timezone=os.getenv("CELERY_TIMEZONE", "UTC"),
    enable_utc=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=86400,
)

logger.info("Celery configured with broker=%s backend=%s", _broker_url(), _backend_url())
