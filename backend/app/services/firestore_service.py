import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from app.config.firebase_config import FirebaseConfig
from app.models.report_schema import ReportStatus
from app.models.queue_schema import AIProcessingStatus, ProcessingStage

logger = logging.getLogger(__name__)


class FirestoreService:
    """Service for managing reports in Firestore and storing images in Firebase Storage."""

    REPORTS_COLLECTION = "reports"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def __init__(self):
        """Initialize Firestore service with database client."""
        try:
            self.db = FirebaseConfig.get_firestore_client()
            self.storage_bucket = FirebaseConfig.get_storage_bucket()
            logger.info("Firestore service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore service: {e}")
            raise

    def generate_report_id(self) -> str:
        """Generate a new report identifier before any persistence occurs."""

        return self._generate_report_id()

    def build_storage_path(self, report_id: str, filename: str) -> str:
        """Build a stable Firebase Storage path for a submitted image."""

        safe_name = Path(filename or "image.jpg").name or "image.jpg"
        return f"reports/{report_id}/{uuid.uuid4().hex}_{safe_name}"

    def create_report(
        self,
        report_id: str,
        location: Dict[str, float],
        image_url: str,
        storage_path: str,
        analysis: Optional[Dict[str, Any]] = None,
        detection_context: Optional[Dict[str, Any]] = None,
        status: ReportStatus = ReportStatus.REPORTED,
        ai_status: AIProcessingStatus = AIProcessingStatus.QUEUED,
        stage: ProcessingStage = ProcessingStage.WAITING,
        progress: int = 0,
        task_id: Optional[str] = None,
        processing_error: Optional[str] = None,
    ) -> str:
        """
        Create a new report document in Firestore.

        Args:
            location: Dictionary with 'latitude' and 'longitude' keys
            analysis: Analysis data from Gemini (issueType, description, etc.)
            image_url: Firebase Storage URL of the uploaded image

        Returns:
            str: Generated report ID

        Raises:
            Exception: If database operation fails
        """
        try:
            report_data = {
                "reportId": report_id,
                "imageUrl": image_url,
                "storagePath": storage_path,
                "location": location,
                "analysis": analysis or {},
                "detectionContext": detection_context or {},
                "status": status.value,
                "ai_status": ai_status.value,
                "stage": stage.value,
                "progress": progress,
                "task_id": task_id,
                "processing_error": processing_error,
                "createdAt": datetime.utcnow(),
                "updatedAt": datetime.utcnow(),
            }

            # Write to Firestore
            self.db.collection(self.REPORTS_COLLECTION).document(report_id).set(report_data)

            logger.info(f"Report created successfully: {report_id}")
            return report_id

        except Exception as e:
            logger.error(f"Error creating report in Firestore: {e}")
            raise

    def get_all_reports(self) -> List[Dict[str, Any]]:
        """
        Retrieve all reports from Firestore.

        Returns:
            List of report dictionaries sorted by creation date (newest first)

        Raises:
            Exception: If database query fails
        """
        try:
            # Query all reports ordered by creation date
            docs = (
                self.db.collection(self.REPORTS_COLLECTION)
                .order_by("createdAt", direction="DESCENDING")
                .stream()
            )

            reports = []
            for doc in docs:
                report = doc.to_dict()
                # Ensure timestamps are in ISO format for JSON serialization
                if isinstance(report.get("createdAt"), datetime):
                    report["createdAt"] = report["createdAt"].isoformat()
                if isinstance(report.get("updatedAt"), datetime):
                    report["updatedAt"] = report["updatedAt"].isoformat()

                reports.append(report)

            logger.info(f"Retrieved {len(reports)} reports from Firestore")
            return reports

        except Exception as e:
            logger.error(f"Error retrieving reports from Firestore: {e}")
            raise

    def get_report_by_id(self, report_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a single report by ID from Firestore.

        Args:
            report_id: The report ID to retrieve

        Returns:
            Report dictionary if found, None otherwise

        Raises:
            Exception: If database query fails
        """
        try:
            doc = self.db.collection(self.REPORTS_COLLECTION).document(report_id).get()

            if not doc.exists:
                logger.warning(f"Report not found: {report_id}")
                return None

            report = doc.to_dict()

            # Ensure timestamps are in ISO format
            if isinstance(report.get("createdAt"), datetime):
                report["createdAt"] = report["createdAt"].isoformat()
            if isinstance(report.get("updatedAt"), datetime):
                report["updatedAt"] = report["updatedAt"].isoformat()

            logger.info(f"Retrieved report: {report_id}")
            return report

        except Exception as e:
            logger.error(f"Error retrieving report {report_id}: {e}")
            raise

    def update_report_status(self, report_id: str, status: ReportStatus) -> Dict[str, Any]:
        """
        Update the status of a report in Firestore.

        Args:
            report_id: The report ID to update
            status: New status value (from ReportStatus enum)

        Returns:
            Updated report dictionary

        Raises:
            ValueError: If report not found
            Exception: If database operation fails
        """
        try:
            # Check if report exists
            doc = self.db.collection(self.REPORTS_COLLECTION).document(report_id).get()

            if not doc.exists:
                logger.warning(f"Report not found for update: {report_id}")
                raise ValueError(f"Report not found: {report_id}")

            # Update status
            update_data = {
                "status": status.value,
                "updatedAt": datetime.utcnow(),
            }

            self.db.collection(self.REPORTS_COLLECTION).document(report_id).update(
                update_data
            )

            logger.info(f"Report status updated: {report_id} -> {status.value}")

            # Return updated report
            return self.get_report_by_id(report_id)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating report status {report_id}: {e}")
            raise

    def update_report_fields(self, report_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Patch a report document and return the updated payload."""

        try:
            doc = self.db.collection(self.REPORTS_COLLECTION).document(report_id).get()

            if not doc.exists:
                logger.warning(f"Report not found for update: {report_id}")
                raise ValueError(f"Report not found: {report_id}")

            normalized_updates = dict(updates)
            normalized_updates["updatedAt"] = datetime.utcnow()

            self.db.collection(self.REPORTS_COLLECTION).document(report_id).update(normalized_updates)

            logger.info("Updated report fields for %s: %s", report_id, ", ".join(sorted(normalized_updates.keys())))
            return self.get_report_by_id(report_id)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating report fields {report_id}: {e}")
            raise

    def update_ai_processing_state(
        self,
        report_id: str,
        *,
        ai_status: Optional[AIProcessingStatus] = None,
        stage: Optional[ProcessingStage] = None,
        progress: Optional[int] = None,
        task_id: Optional[str] = None,
        processing_error: Optional[str] = None,
        analysis: Optional[Dict[str, Any]] = None,
        detection_context: Optional[Dict[str, Any]] = None,
        ai_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update only the async AI lifecycle fields."""

        updates: Dict[str, Any] = {}

        if ai_status is not None:
            updates["ai_status"] = ai_status.value
        if stage is not None:
            updates["stage"] = stage.value
        if progress is not None:
            updates["progress"] = progress
        if task_id is not None:
            updates["task_id"] = task_id
        if processing_error is not None:
            updates["processing_error"] = processing_error
        if analysis is not None:
            updates["analysis"] = analysis
        if detection_context is not None:
            updates["detectionContext"] = detection_context
        if ai_metadata is not None:
            updates["ai_metadata"] = ai_metadata

        if not updates:
            return self.get_report_by_id(report_id)

        return self.update_report_fields(report_id, updates)

    def mark_ai_queue_failed(self, report_id: str, error_message: str) -> Dict[str, Any]:
        """Record that the report was stored successfully but queue dispatch failed."""

        return self.update_ai_processing_state(
            report_id,
            ai_status=AIProcessingStatus.FAILED,
            stage=ProcessingStage.QUEUE_FAILED,
            progress=0,
            processing_error=error_message,
        )

    def download_image_from_storage(self, storage_path: str) -> bytes:
        """Download a report image from Firebase Storage for worker-side AI processing."""

        if not self.storage_bucket:
            raise ValueError(
                "Firebase Storage not configured. "
                "Set FIREBASE_STORAGE_BUCKET environment variable."
            )

        if not storage_path:
            raise ValueError("Storage path is required to download a report image")

        blob = self.storage_bucket.blob(storage_path)
        return blob.download_as_bytes()

    def upload_image_to_storage(
        self,
        image_bytes: bytes,
        filename: str,
        blob_name: Optional[str] = None,
        content_type: str = "image/jpeg",
    ) -> str:
        """
        Upload an image to Firebase Storage.

        Args:
            image_bytes: Image file content as bytes
            filename: Original filename (used for content type detection)

        Returns:
            str: Public URL of the uploaded image

        Raises:
            ValueError: If storage not configured or upload fails
            Exception: For storage operation errors
        """
        try:
            if not self.storage_bucket:
                logger.error("Firebase Storage not configured")
                raise ValueError(
                    "Firebase Storage not configured. "
                    "Set FIREBASE_STORAGE_BUCKET environment variable."
                )

            # Check file size
            if len(image_bytes) > self.MAX_FILE_SIZE:
                logger.warning(f"Image size {len(image_bytes)} exceeds max {self.MAX_FILE_SIZE}")
                raise ValueError(f"File size exceeds maximum allowed size of {self.MAX_FILE_SIZE} bytes")

            # Generate a stable blob name so workers can fetch the exact asset later.
            blob_name = blob_name or self.build_storage_path(self._generate_report_id(), filename)

            # Upload to Storage
            blob = self.storage_bucket.blob(blob_name)
            blob.upload_from_string(image_bytes, content_type=content_type)

            # Make blob public and get URL
            blob.make_public()
            image_url = blob.public_url

            logger.info(f"Image uploaded successfully: {blob_name}")
            return image_url

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error uploading image to Firebase Storage: {e}")
            raise

    def _generate_report_id(self) -> str:
        """
        Generate a unique report ID.

        Returns:
            str: Unique report ID with format "rpt_<uuid>"
        """
        return f"rpt_{uuid.uuid4().hex[:12]}"
