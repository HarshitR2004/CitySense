"""Shared logging configuration for the API and Celery worker processes."""

from __future__ import annotations

import logging
import os
from typing import Optional


def configure_logging(level: Optional[str] = None) -> None:
    """Configure a consistent log format once per process."""

    if getattr(configure_logging, "_configured", False):
        return

    log_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(processName)s | %(message)s",
    )

    configure_logging._configured = True  # type: ignore[attr-defined]
