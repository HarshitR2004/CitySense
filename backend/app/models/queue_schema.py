"""Schemas for the async report submission and AI processing queue."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ReportLifecycleStatus(str, Enum):
    """Lifecycle state of the report record itself."""

    REPORTED = "reported"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AIProcessingStatus(str, Enum):
    """Lifecycle state for the background AI pipeline."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStage(str, Enum):
    """Fine-grained processing stage used for Firestore progress updates."""

    WAITING = "waiting"
    QUEUED = "queued"
    DOWNLOADING = "downloading"
    DETECTING = "detecting"
    REASONING = "reasoning"
    ENRICHING = "enriching"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    QUEUE_FAILED = "queue_failed"


class ReportSubmissionResponse(BaseModel):
    """Immediate response returned after the report is safely persisted."""

    success: bool = Field(default=True, description="Whether the submission was accepted")
    report_id: str = Field(..., description="Generated report identifier")
    message: str = Field(..., description="Human-readable confirmation message")
    ai_status: AIProcessingStatus = Field(
        default=AIProcessingStatus.QUEUED,
        description="Current AI processing state",
    )
    stage: ProcessingStage = Field(
        default=ProcessingStage.WAITING,
        description="Current AI processing stage",
    )
    task_id: Optional[str] = Field(
        default=None,
        description="Celery task identifier, if enqueued successfully",
    )
