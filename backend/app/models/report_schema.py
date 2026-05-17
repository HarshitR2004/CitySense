from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, validator


# ============================================
# Enums
# ============================================

class IssueType(str, Enum):
    """Types of civic infrastructure issues that can be reported."""

    POTHOLE = "pothole"
    GARBAGE_ACCUMULATION = "garbage_accumulation"
    ROAD_DAMAGE = "road_damage"
    WATERLOGGING = "waterlogging"
    BROKEN_INFRASTRUCTURE = "broken_infrastructure"
    OTHER = "other"


class ReportStatus(str, Enum):
    """Lifecycle status of a report record."""

    REPORTED = "reported"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AIProcessingStatus(str, Enum):
    """Lifecycle status for background AI processing."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingStage(str, Enum):
    """Fine-grained stage of the async AI pipeline."""

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


class UrgencyLevel(str, Enum):
    """Urgency level of the reported issue."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


# ============================================
# Location Models
# ============================================

class Location(BaseModel):
    """Geographical location of the reported issue."""

    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        description="Latitude coordinate (-90 to 90)"
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        description="Longitude coordinate (-180 to 180)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }


# ============================================
# Gemini Analysis Response Model
# ============================================

class GeminiAnalysisResponse(BaseModel):
    """Structured response from Gemini Vision API analysis."""

    issueType: str = Field(
        ...,
        description="Type of infrastructure issue detected"
    )
    description: str = Field(
        ...,
        description="Detailed description of the issue"
    )
    impact: str = Field(
        ...,
        description="Public safety and urban impact assessment"
    )
    suggestedAction: str = Field(
        ...,
        description="Recommended municipal action"
    )
    urgency: str = Field(
        ...,
        description="Urgency level (Low, Medium, High, Critical)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "issueType": "pothole",
                "description": "Large pothole approximately 2 feet in diameter",
                "impact": "High risk of vehicle damage and accidents",
                "suggestedAction": "Immediate road repair needed",
                "urgency": "High"
            }
        }


# ============================================
# API Request Models
# ============================================

class ReportUpdateRequest(BaseModel):
    """Request body for updating a report status."""

    status: ReportStatus = Field(
        ...,
        description="New status for the report"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "In Progress"
            }
        }


# ============================================
# API Response Models
# ============================================

class ReportResponse(BaseModel):
    """Complete report response with all metadata."""

    reportId: str = Field(
        ...,
        description="Unique identifier for the report"
    )
    imageUrl: str = Field(
        ...,
        description="Firebase Storage URL of the uploaded image"
    )
    location: Location = Field(
        ...,
        description="Geographical location where issue was reported"
    )
    analysis: Optional[GeminiAnalysisResponse] = Field(
        default=None,
        description="AI-generated analysis of the infrastructure issue"
    )
    status: ReportStatus = Field(
        default=ReportStatus.REPORTED,
        description="Current status in the municipal workflow"
    )
    ai_status: AIProcessingStatus = Field(
        default=AIProcessingStatus.QUEUED,
        description="Current async AI processing status"
    )
    stage: ProcessingStage = Field(
        default=ProcessingStage.WAITING,
        description="Current stage in the AI processing pipeline"
    )
    progress: int = Field(
        0,
        ge=0,
        le=100,
        description="Processing progress percentage"
    )
    task_id: Optional[str] = Field(
        None,
        description="Celery task identifier"
    )
    processing_error: Optional[str] = Field(
        None,
        description="Latest processing error, if any"
    )
    createdAt: datetime = Field(
        ...,
        description="Timestamp when report was created"
    )
    updatedAt: Optional[datetime] = Field(
        None,
        description="Timestamp when report was last updated"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reportId": "rpt_abc123def456",
                "imageUrl": "https://firebase-storage-url.com/image.jpg",
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060
                },
                "analysis": {
                    "issueType": "pothole",
                    "description": "Large pothole approximately 2 feet in diameter",
                    "impact": "High risk of vehicle damage and accidents",
                    "suggestedAction": "Immediate road repair needed",
                    "urgency": "High"
                },
                "status": "Pending",
                "createdAt": "2024-01-15T10:30:00Z"
            }
        }


class ReportListResponse(BaseModel):
    """Response for GET /reports endpoint."""

    reports: list[ReportResponse] = Field(
        ...,
        description="List of all reports"
    )
    count: int = Field(
        ...,
        description="Total number of reports"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "reports": [],
                "count": 0
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(
        ...,
        description="Error message"
    )
    detail: Optional[str] = Field(
        None,
        description="Additional error details (only in debug mode)"
    )
    code: Optional[str] = Field(
        None,
        description="Error code for programmatic handling"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Unable to process image",
                "detail": None,
                "code": "ANALYSIS_FAILED"
            }
        }


class HealthCheckResponse(BaseModel):
    """Response for health check endpoint."""

    status: str = Field(
        ...,
        description="Health status"
    )
    version: str = Field(
        ...,
        description="API version"
    )
    timestamp: datetime = Field(
        ...,
        description="Server timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }
