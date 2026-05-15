"""
Report Processing Service.

Orchestrates the workflow of detecting issues with YOLOv8, grounding Gemini's
reasoning on the detections, storing the image, and creating the report.
"""

import asyncio
import logging
from typing import Dict, Any

from app.services.gemini_service import GeminiService
from app.services.firestore_service import FirestoreService
from app.services.yolo_service import YOLOService

logger = logging.getLogger(__name__)


class ReportService:
    """Orchestrates the complete workflow for image analysis and report generation."""

    def __init__(self):
        """Initialize report service with dependent services."""
        try:
            logger.info("Initializing ReportService")

            # Load the visual grounding model first so the service fails fast if
            # the trained weights are missing or invalid.
            self.yolo_service = YOLOService()

            # Gemini now reasons over YOLO output instead of independently
            # classifying the image, which reduces hallucinated issue types.
            self.gemini_service = GeminiService()

            self.firestore_service = FirestoreService()

            logger.info("Report service initialized")

        except Exception as e:
            logger.error(f"Failed to initialize Report service: {e}")
            raise

    def process_image_and_generate_report(
        self,
        image_bytes: bytes,
        latitude: float,
        longitude: float,
        original_filename: str = "image.jpg"
    ) -> Dict[str, Any]:
        """
        Process an image and generate a structured municipal report.

        Workflow:
        1. Run YOLOv8 inference and filter low-confidence detections
        2. Ground Gemini reasoning on the YOLO detections
        3. Upload image to Firebase Storage
        4. Create report document in Firestore
        5. Return structured response

        Args:
            image_bytes: Image file content as bytes
            latitude: Latitude coordinate of the issue location
            longitude: Longitude coordinate of the issue location
            original_filename: Original filename for storage purposes

        Returns:
            dict: Complete report data including analysis and metadata

        Raises:
            ValueError: For invalid input or processing errors
            Exception: For service failures
        """
        try:
            logger.info(f"Starting image processing for {original_filename}")

            # Step 1: Detect and localize visible issues with the trained YOLOv8 model.
            logger.debug("Step 1: Running YOLOv8 inference")
            yolo_result = self.yolo_service.analyze_image(image_bytes)
            detection_context = self.yolo_service.build_gemini_context(yolo_result)
            logger.info(
                "YOLO grounding complete: %s detection(s), primary issue type=%s",
                len(detection_context.get("detected_objects", [])),
                detection_context.get("primary_issue_type"),
            )

            # Step 2: Ask Gemini to reason over the structured detections instead
            # of making an independent visual classification.
            logger.debug("Step 2: Calling Gemini with grounded detection context")
            analysis = self.gemini_service.analyze_detections(detection_context)
            logger.info("Gemini reasoning complete: %s", analysis.get("issueType"))

            # Step 3: Persist the original image for dashboard and review workflows.
            logger.debug("Step 3: Uploading image to Firebase Storage")
            image_url = self.firestore_service.upload_image_to_storage(
                image_bytes, original_filename
            )
            logger.info(f"Image uploaded to Storage: {image_url}")

            # Step 4: Save the report, keeping the YOLO context alongside the Gemini analysis.
            logger.debug("Step 4: Creating report in Firestore")
            location = {
                "latitude": latitude,
                "longitude": longitude
            }

            report_id = self.firestore_service.create_report(
                location=location,
                analysis=analysis,
                image_url=image_url,
                detection_context=detection_context,
            )
            logger.info(f"Report created in Firestore: {report_id}")

            # Step 5: Retrieve and return the persisted report record.
            logger.debug("Step 5: Fetching final report data")
            report_data = self.firestore_service.get_report_by_id(report_id)

            logger.info(f"Image processing completed successfully: {report_id}")
            return report_data

        except ValueError as e:
            logger.error(f"Validation error during report processing: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing image and generating report: {e}")
            raise

    async def process_image_and_generate_report_async(
        self,
        image_bytes: bytes,
        latitude: float,
        longitude: float,
        original_filename: str = "image.jpg",
    ) -> Dict[str, Any]:
        """Async wrapper for the full pipeline to support request offloading."""

        return await asyncio.to_thread(
            self.process_image_and_generate_report,
            image_bytes,
            latitude,
            longitude,
            original_filename,
        )

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

            # Validate status
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
