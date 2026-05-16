"""Worker-side AI pipeline for CitySense report enrichment."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from app.models.queue_schema import AIProcessingStatus, ProcessingStage
from app.services.firestore_service import FirestoreService
from app.services.gemini_service import GeminiService
from app.services.yolo_service import YOLOService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SeverityProfile:
    score: int
    level: str


class AIProcessingService:
    """Encapsulates the expensive AI workflow executed by Celery workers."""

    _shared_yolo_service: Optional[YOLOService] = None
    _shared_gemini_service: Optional[GeminiService] = None

    def __init__(self) -> None:
        self.firestore_service = FirestoreService()

        if AIProcessingService._shared_yolo_service is None:
            AIProcessingService._shared_yolo_service = YOLOService()
        if AIProcessingService._shared_gemini_service is None:
            AIProcessingService._shared_gemini_service = GeminiService()

        self.yolo_service = AIProcessingService._shared_yolo_service
        self.gemini_service = AIProcessingService._shared_gemini_service

    def process_report(self, report_id: str) -> Dict[str, Any]:
        """Run the full AI pipeline for a submitted report."""

        report = self.firestore_service.get_report_by_id(report_id)
        if not report:
            raise ValueError(f"Report not found: {report_id}")

        storage_path = report.get("storagePath")
        if not storage_path:
            raise ValueError(f"Report {report_id} is missing the storagePath field")

        self.firestore_service.update_ai_processing_state(
            report_id,
            ai_status=AIProcessingStatus.PROCESSING,
            stage=ProcessingStage.DOWNLOADING,
            progress=10,
            processing_error=None,
        )

        image_bytes = self.firestore_service.download_image_from_storage(storage_path)

        self.firestore_service.update_ai_processing_state(
            report_id,
            stage=ProcessingStage.DETECTING,
            progress=35,
        )

        yolo_result = self.yolo_service.analyze_image(image_bytes)
        detection_context = self.yolo_service.build_gemini_context(yolo_result)

        self.firestore_service.update_ai_processing_state(
            report_id,
            stage=ProcessingStage.REASONING,
            progress=60,
            detection_context=detection_context,
        )

        analysis = self.gemini_service.analyze_detections(detection_context)
        enrichment = self._build_enrichment(analysis, detection_context)

        self.firestore_service.update_ai_processing_state(
            report_id,
            ai_status=AIProcessingStatus.COMPLETED,
            stage=ProcessingStage.ENRICHING,
            progress=90,
            analysis=analysis,
            detection_context=detection_context,
            ai_metadata=enrichment,
        )

        updated_report = self.firestore_service.update_ai_processing_state(
            report_id,
            ai_status=AIProcessingStatus.COMPLETED,
            stage=ProcessingStage.COMPLETED,
            progress=100,
            analysis=analysis,
            detection_context=detection_context,
            ai_metadata=enrichment,
        )

        return updated_report

    def mark_failed(self, report_id: str, error: Exception | str) -> Dict[str, Any]:
        """Persist a failure state without touching the report lifecycle status."""

        error_message = str(error)
        logger.error("AI processing failed for %s: %s", report_id, error_message, exc_info=isinstance(error, Exception))

        return self.firestore_service.update_ai_processing_state(
            report_id,
            ai_status=AIProcessingStatus.FAILED,
            stage=ProcessingStage.FAILED,
            progress=0,
            processing_error=error_message,
        )

    def _build_enrichment(self, analysis: Dict[str, Any], detection_context: Dict[str, Any]) -> Dict[str, Any]:
        """Derive lightweight operational metadata from the AI output."""

        urgency = str(analysis.get("urgency", "Low"))
        severity = self._severity_profile_for_urgency(urgency)

        return {
            "severityScore": severity.score,
            "severityLevel": severity.level,
            "primaryIssueType": detection_context.get("primary_issue_type", "other"),
            "detectedObjects": len(detection_context.get("detected_objects", [])),
        }

    def _severity_profile_for_urgency(self, urgency: str) -> SeverityProfile:
        urgency_key = urgency.strip().lower()

        if urgency_key == "critical":
            return SeverityProfile(score=95, level="critical")
        if urgency_key == "high":
            return SeverityProfile(score=75, level="high")
        if urgency_key == "medium":
            return SeverityProfile(score=50, level="medium")
        return SeverityProfile(score=25, level="low")
