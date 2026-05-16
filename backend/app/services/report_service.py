"""Report ingestion service for the immediate submission path."""

import asyncio
import logging
from typing import Dict, Any, Optional

from app.core.celery_app import celery_app
from app.models.queue_schema import AIProcessingStatus, ProcessingStage, ReportSubmissionResponse
from app.models.report_schema import ReportStatus
from app.services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)


class ReportService:
    """Handles the durable submit path and Celery task dispatch."""

    def __init__(self):
        """Initialize report service with Firestore only.

        The AI services are intentionally not loaded here so the API layer stays
        lightweight and never performs YOLO/Gemini work on the request thread.
        """

        try:
            self.firestore_service = FirestoreService()

            logger.info("Report service initialized for async ingestion")

        except Exception as e:
            logger.error(f"Failed to initialize Report service: {e}")
            raise

    def submit_report(
        self,
        image_bytes: bytes,
        latitude: float,
        longitude: float,
        original_filename: str = "image.jpg",
        content_type: str = "image/jpeg",
    ) -> Dict[str, Any]:
        """
        Persist the submission immediately and enqueue the AI pipeline.

        This method is intentionally split from the Celery worker path. It only
        handles the durable user-facing submission and queue dispatch.

        Args:
            image_bytes: Image file content as bytes
            latitude: Latitude coordinate of the issue location
            longitude: Longitude coordinate of the issue location
            original_filename: Original filename for storage purposes

        Returns:
            dict: Submission response including the generated report ID and task ID

        Raises:
            ValueError: For invalid input
            Exception: For storage or Firestore failures
        """
        try:
            logger.info("Submitting report for %s", original_filename)

            report_id = self.firestore_service.generate_report_id()
            location = {
                "latitude": latitude,
                "longitude": longitude
            }

            storage_path = self.firestore_service.build_storage_path(report_id, original_filename)
            image_url = self.firestore_service.upload_image_to_storage(
                image_bytes,
                original_filename,
                blob_name=storage_path,
                content_type=content_type,
            )

            self.firestore_service.create_report(
                report_id=report_id,
                location=location,
                image_url=image_url,
                storage_path=storage_path,
                analysis={},
                detection_context={},
                status=ReportStatus.REPORTED,
                ai_status=AIProcessingStatus.QUEUED,
                stage=ProcessingStage.WAITING,
                progress=0,
            )

            logger.info("Report persisted with id=%s, storage_path=%s", report_id, storage_path)

            task_id: Optional[str] = None

            try:
                async_result = celery_app.send_task("citysense.process_report_ai", args=[report_id])
                task_id = async_result.id

                self.firestore_service.update_ai_processing_state(
                    report_id,
                    ai_status=AIProcessingStatus.QUEUED,
                    stage=ProcessingStage.QUEUED,
                    progress=0,
                    task_id=task_id,
                )

            except Exception as queue_error:
                logger.error("Failed to enqueue AI task for %s: %s", report_id, queue_error, exc_info=True)
                self.firestore_service.mark_ai_queue_failed(report_id, str(queue_error))

            submission = ReportSubmissionResponse(
                report_id=report_id,
                message="Issue reported successfully",
                ai_status=AIProcessingStatus.QUEUED if task_id else AIProcessingStatus.FAILED,
                stage=ProcessingStage.QUEUED if task_id else ProcessingStage.QUEUE_FAILED,
                task_id=task_id,
            )

            return submission.model_dump()

        except ValueError as e:
            logger.error(f"Validation error during report processing: {e}")
            raise
        except Exception as e:
            logger.error(f"Error submitting report: {e}")
            raise

    async def process_image_and_generate_report_async(
        self,
        image_bytes: bytes,
        latitude: float,
        longitude: float,
        original_filename: str = "image.jpg",
        content_type: str = "image/jpeg",
    ) -> Dict[str, Any]:
        """Async wrapper for the submit path to keep the FastAPI handler non-blocking."""

        return await asyncio.to_thread(
            self.submit_report,
            image_bytes,
            latitude,
            longitude,
            original_filename,
            content_type,
        )

    def process_image_and_generate_report(
        self,
        image_bytes: bytes,
        latitude: float,
        longitude: float,
        original_filename: str = "image.jpg",
        content_type: str = "image/jpeg",
    ) -> Dict[str, Any]:
        """Backward-facing alias for the new submit path."""

        return self.submit_report(image_bytes, latitude, longitude, original_filename, content_type)

    def get_all_reports(self) -> list:
        """
        Retrieve all reports from Firestore.

        Returns:
            list: List of all reports sorted by creation date (newest first)

        Raises:
            Exception: If database query fails
        """
        try:
            reports = self.firestore_service.get_all_reports()
            logger.info(f"Retrieved {len(reports)} reports")
            return reports
        except Exception as e:
            logger.error(f"Error retrieving reports: {e}")
            raise

    def get_report_by_id(self, report_id: str) -> Dict[str, Any]:
        """
        Retrieve a single report by ID.

        Args:
            report_id: The report ID to retrieve

        Returns:
            dict: Report data

        Raises:
            ValueError: If report not found
            Exception: If database query fails
        """
        try:
            report = self.firestore_service.get_report_by_id(report_id)

            if not report:
                logger.warning(f"Report not found: {report_id}")
                raise ValueError(f"Report not found: {report_id}")

            return report

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving report {report_id}: {e}")
            raise

    def update_report_status(self, report_id: str, status: str) -> Dict[str, Any]:
        """
        Update the status of a report.

        Args:
            report_id: The report ID to update
            status: New status value (Pending, In Progress, or Resolved)

        Returns:
            dict: Updated report data

        Raises:
            ValueError: If report not found or invalid status
            Exception: If database operation fails
        """
        try:
            from app.models.report_schema import ReportStatus

            try:
                status_enum = ReportStatus(status)
            except ValueError:
                logger.error(f"Invalid status value: {status}")
                raise ValueError(f"Invalid status. Must be one of: {', '.join([s.value for s in ReportStatus])}")

            updated_report = self.firestore_service.update_report_status(report_id, status_enum)
            logger.info(f"Report status updated: {report_id} -> {status}")

            return updated_report

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating report status: {e}")
            raise
