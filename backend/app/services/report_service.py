"""
Report Processing Service

Orchestrates the workflow of analyzing images, storing them, and creating reports.
This service coordinates between GeminiService and FirestoreService.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Dict, Any

from app.models.report_schema import ReportResponse, GeminiAnalysisResponse
from app.services.gemini_service import GeminiService
from app.services.firestore_service import FirestoreService

logger = logging.getLogger(__name__)


class ReportService:
    """Orchestrates the complete workflow for image analysis and report generation."""

    def __init__(self):
        """Initialize report service with dependent services."""
        try:
            print("[DEBUG INIT] Initializing ReportService...")
            print("[DEBUG INIT] Setting up GeminiService...")
            self.gemini_service = GeminiService()
            
            print("[DEBUG INIT] Setting up FirestoreService...")
            self.firestore_service = FirestoreService()
            
            self.temp_upload_dir = "backend/temp_uploads"

            # Ensure temp directory exists
            print(f"[DEBUG INIT] Verifying temp directory at {self.temp_upload_dir}...")
            Path(self.temp_upload_dir).mkdir(parents=True, exist_ok=True)
            
            print("[DEBUG INIT] ReportService initialized successfully!")
            logger.info("Report service initialized")

        except Exception as e:
            print(f"[DEBUG INIT ERROR] Failed to initialize ReportService: {e}")
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
        1. Analyze image using Gemini Vision API
        2. Upload image to Firebase Storage
        3. Create report document in Firestore
        4. Return structured response

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
        temp_file_path = None

        try:
            print(f"\n[DEBUG PIPELINE] Starting processing for {original_filename}")
            logger.info(f"Starting image processing for {original_filename}")

            # Step 1: Analyze image with Gemini Vision API
            print("[DEBUG PIPELINE] Step 1: Calling Gemini Vision API...")
            logger.debug("Step 1: Analyzing image with Gemini Vision API")
            analysis = self.gemini_service.analyze_image(image_bytes)
            print(f"[DEBUG PIPELINE] Step 1 Complete - Detected Issue: {analysis.get('issueType')}")
            logger.info(f"Image analysis complete: {analysis.get('issueType')}")

            # Step 2: Upload image to Firebase Storage
            print("[DEBUG PIPELINE] Step 2: Uploading image to Firebase Storage...")
            logger.debug("Step 2: Uploading image to Firebase Storage")
            image_url = self.firestore_service.upload_image_to_storage(
                image_bytes, original_filename
            )
            print(f"[DEBUG PIPELINE] Step 2 Complete - Image URL: {image_url[:30]}...")
            logger.info(f"Image uploaded to Storage: {image_url}")

            # Step 3: Create report in Firestore
            print("[DEBUG PIPELINE] Step 3: Saving report to Firestore...")
            logger.debug("Step 3: Creating report in Firestore")
            location = {
                "latitude": latitude,
                "longitude": longitude
            }

            report_id = self.firestore_service.create_report(
                location=location,
                analysis=analysis,
                image_url=image_url
            )
            print(f"[DEBUG PIPELINE] Step 3 Complete - Report created with ID: {report_id}")
            logger.info(f"Report created in Firestore: {report_id}")

            # Step 4: Retrieve and return complete report
            print("[DEBUG PIPELINE] Step 4: Fetching final report data...")
            report_data = self.firestore_service.get_report_by_id(report_id)

            print(f"[DEBUG PIPELINE] Pipeline finished successfully for report {report_id}\n")
            logger.info(f"Image processing completed successfully: {report_id}")
            return report_data

        except ValueError as e:
            logger.error(f"Validation error during report processing: {e}")
            raise
        except Exception as e:
            logger.error(f"Error processing image and generating report: {e}")
            raise
        finally:
            # Cleanup temporary files if created
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                    logger.debug(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {temp_file_path}: {e}")

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
