import logging
import asyncio
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from app.models.queue_schema import ReportSubmissionResponse
from app.services.report_service import ReportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["reports"])

# Initialize report service
try:
    report_service = ReportService()
except Exception as e:
    logger.error(f"Failed to initialize report service in routes: {e}")
    report_service = None


@router.post(
    "/analyze",
    response_model=ReportSubmissionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload image and generate infrastructure report",
    description="Accept an image of a civic infrastructure issue along with location metadata. "
                "Persist the report immediately, then queue YOLOv8 and Gemini processing in the background.",
    responses={
        202: {"description": "Report accepted and queued for background processing"},
        400: {"description": "Invalid input or file format"},
        500: {"description": "Server error during processing"},
    }
)
async def analyze_image(
    file: UploadFile = File(..., description="Image file (JPEG/PNG, max 10MB)"),
    latitude: float = Form(..., ge=-90, le=90, description="Latitude coordinate"),
    longitude: float = Form(..., ge=-180, le=180, description="Longitude coordinate"),
):
    """
    Upload an image and generate a structured civic infrastructure report.

    **Request:**
    - `file`: Image file (multipart form upload)
    - `latitude`: Latitude of issue location
    - `longitude`: Longitude of issue location

    **Response:**
    - `reportId`: Unique report identifier
    - `imageUrl`: Firebase Storage URL of image
    - `location`: Coordinates of reported issue
    - `analysis`: Gemini Vision analysis results
    - `status`: Current report status (default: Pending)
    - `createdAt`: Report creation timestamp

    **Error Codes:**
    - `INVALID_FILE`: File format not supported
    - `FILE_TOO_LARGE`: File exceeds size limit
    - `ANALYSIS_FAILED`: Image analysis error
    - `STORAGE_ERROR`: Firebase Storage error
    - `DATABASE_ERROR`: Firestore error
    """
    try:
        # Check if report service is initialized
        if not report_service:
            logger.error("Report service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend services not properly configured. Check Firebase credentials and API keys.",
            )
        
        # Validate file type
        allowed_types = {"image/jpeg", "image/png", "image/jpg"}
        if file.content_type not in allowed_types:
            logger.warning(f"Invalid file type: {file.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_types)}",
            )

        # Read file content
        file_content = await file.read()

        if not file_content:
            logger.warning("Empty file uploaded")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty",
            )

        # Check file size
        max_size = 10 * 1024 * 1024
        if len(file_content) > max_size:
            logger.warning(f"File too large: {len(file_content)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {max_size} bytes",
            )

        # Process image and generate report
        logger.info(f"Processing image: {file.filename} at ({latitude}, {longitude})")
        
        
        report_data = await asyncio.to_thread(
                report_service.submit_report,
                file_content,
                latitude,
                longitude,
                file.filename or "image.jpg",
                file.content_type or "image/jpeg",
            )

        return ReportSubmissionResponse(**report_data)        

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Unexpected error during image analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process image and generate report",
        )


