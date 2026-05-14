

import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.config.firebase_config import FirebaseConfig
from app.models.report_schema import ReportStatus

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

    def create_report(
        self,
        location: Dict[str, float],
        analysis: Dict[str, Any],
        image_url: str
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
            report_id = self._generate_report_id()

            report_data = {
                "reportId": report_id,
                "imageUrl": image_url,
                "location": location,
                "analysis": analysis,
                "status": ReportStatus.PENDING.value,
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

    def upload_image_to_storage(self, image_bytes: bytes, filename: str) -> str:
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

            # Generate unique blob name
            blob_name = f"reports/{uuid.uuid4()}/{filename}"

            # Upload to Storage
            blob = self.storage_bucket.blob(blob_name)
            blob.upload_from_string(image_bytes, content_type="image/jpeg")

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
