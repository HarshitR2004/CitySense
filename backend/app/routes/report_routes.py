import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from app.models.report_schema import (
    ReportResponse,
    ReportListResponse,
    ReportUpdateRequest,
    ErrorResponse,
)
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


# ============================================
# POST /analyze - Analyze Image and Generate Report
# ============================================

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

        # Check file size (10MB limit)
        max_size = 10 * 1024 * 1024
        if len(file_content) > max_size:
            logger.warning(f"File too large: {len(file_content)} bytes")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {max_size} bytes",
            )

        # Process image and generate report
        logger.info(f"Processing image: {file.filename} at ({latitude}, {longitude})")

        report_data = await report_service.process_image_and_generate_report_async(
            image_bytes=file_content,
            latitude=latitude,
            longitude=longitude,
            original_filename=file.filename or "image.jpg",
            content_type=file.content_type or "image/jpeg",
        )

        logger.info(f"Report accepted: {report_data.get('report_id')}")
        return ReportSubmissionResponse(**report_data)

    except HTTPException:
        raise

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


# ============================================
# GET /reports - Retrieve All Reports
# ============================================

@router.get(
    "/reports",
    response_model=ReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve all reports",
    description="Fetch all civic infrastructure reports from the database. "
                "Returns reports sorted by creation date (newest first).",
    responses={
        200: {"description": "Reports retrieved successfully"},
        500: {"description": "Server error retrieving reports"},
    }
)
async def get_all_reports():
    """
    Retrieve all reports from the system.

    **Response:**
    - `reports`: Array of report objects
    - `count`: Total number of reports

    Each report contains:
    - `reportId`: Unique identifier
    - `imageUrl`: Image storage URL
    - `location`: Issue coordinates
    - `analysis`: Analysis results from Gemini
    - `status`: Current status (Pending, In Progress, Resolved)
    - `createdAt`: Report creation time
    """
    try:
        # Check if report service is initialized
        if not report_service:
            logger.error("Report service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend services not properly configured.",
            )
        
        logger.info("Retrieving all reports")
        reports = report_service.get_all_reports()

        return ReportListResponse(
            reports=[ReportResponse(**report) for report in reports],
            count=len(reports)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving reports: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve reports",
        )


# ============================================
# GET /reports/{report_id} - Retrieve Single Report
# ============================================

@router.get(
    "/reports/{report_id}",
    response_model=ReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a single report",
    description="Fetch a specific report by ID.",
    responses={
        200: {"description": "Report retrieved successfully"},
        404: {"description": "Report not found"},
        500: {"description": "Server error"},
    }
)
async def get_report(report_id: str):
    """
    Retrieve a specific report by ID.

    **Path Parameters:**
    - `report_id`: The report ID to retrieve

    **Response:**
    - Complete report object with all metadata and analysis

    **Error Codes:**
    - `NOT_FOUND`: Report ID not found
    - `DATABASE_ERROR`: Query failed
    """
    try:
        # Check if report service is initialized
        if not report_service:
            logger.error("Report service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend services not properly configured.",
            )
        
        logger.info(f"Retrieving report: {report_id}")
        report_data = report_service.get_report_by_id(report_id)

        return ReportResponse(**report_data)

    except HTTPException:
        raise
    except ValueError:
        logger.warning(f"Report not found: {report_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report not found: {report_id}",
        )

    except Exception as e:
        logger.error(f"Error retrieving report {report_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve report",
        )


# ============================================
# PATCH /reports/{report_id} - Update Report Status
# ============================================

@router.patch(
    "/reports/{report_id}",
    response_model=ReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Update report status",
    description="Update the status of a report in the municipal workflow.",
    responses={
        200: {"description": "Report updated successfully"},
        400: {"description": "Invalid status value"},
        404: {"description": "Report not found"},
        500: {"description": "Server error"},
    }
)
async def update_report_status(
    report_id: str,
    request: ReportUpdateRequest,
):
    """
    Update the status of a civic infrastructure report.

    **Path Parameters:**
    - `report_id`: The report ID to update

    **Request Body:**
    - `status`: New status (Pending, In Progress, Resolved)

    **Response:**
    - Updated report object with new status and updatedAt timestamp

    **Example Request:**
    ```json
    {
      "status": "In Progress"
    }
    ```

    **Error Codes:**
    - `INVALID_STATUS`: Status not one of allowed values
    - `NOT_FOUND`: Report ID not found
    - `DATABASE_ERROR`: Update failed
    """
    try:
        # Check if report service is initialized
        if not report_service:
            logger.error("Report service not initialized")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Backend services not properly configured.",
            )
        
        logger.info(f"Updating report status: {report_id} -> {request.status}")

        updated_report = report_service.update_report_status(
            report_id=report_id,
            status=request.status.value
        )

        logger.info(f"Report status updated successfully: {report_id}")
        return ReportResponse(**updated_report)

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error updating report {report_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update report status",
        )
