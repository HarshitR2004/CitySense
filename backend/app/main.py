"""
FastAPI Application Entry Point

Main application setup with CORS, middleware, exception handlers, and route registration.
"""

# Load environment variables first
from dotenv import load_dotenv
load_dotenv()

import logging
import os
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.logging_config import configure_logging
from app.models.report_schema import HealthCheckResponse
from app.routes import report_routes

# ============================================
# Logging Configuration
# ============================================

configure_logging()
logger = logging.getLogger(__name__)


# ============================================
# Lifespan Events
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    
    Startup:
    - Create temp_uploads directory
    - Initialize services
    
    Shutdown:
    - Cleanup (placeholder for future)
    """
    # Startup
    logger.info("Starting up CitySense Backend...")
    
    # Create temp_uploads directory
    temp_dir = Path("backend/temp_uploads")
    temp_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Temp uploads directory ready: {temp_dir}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CitySense Backend...")
    logger.info("Application shutdown complete")


# ============================================
# FastAPI Application
# ============================================

app = FastAPI(
    title="CitySense Backend API",
    description="AI-powered civic infrastructure reporting system using FastAPI, Redis, Celery, Firebase, and grounded Gemini/YOLO background processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

logger.info("FastAPI application initialized")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# Request Logging Middleware
# ============================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests and responses."""
    logger.info(f"{request.method} {request.url.path}")
    
    response = await call_next(request)
    
    logger.info(f"{request.method} {request.url.path} - {response.status_code}")
    return response


# ============================================
# Exception Handlers
# ============================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    Returns generic error message to client, logs details.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG") == "True" else None,
            "code": "INTERNAL_ERROR",
        }
    )


# ============================================
# Health Check Endpoint
# ============================================

@app.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    tags=["health"],
)
async def health_check():
    """
    Simple health check endpoint to verify API is running.
    
    Returns:
    - `status`: "healthy" if service is operational
    - `version`: API version
    - `timestamp`: Current server timestamp
    """
    logger.debug("Health check requested")
    
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )


# ============================================
# Root Endpoint
# ============================================

@app.get(
    "/",
    summary="API Information",
    tags=["info"],
)
async def root():
    """
    Root endpoint providing API information and links.
    """
    return {
        "service": "CitySense Backend",
        "version": "1.0.0",
        "description": "AI-powered civic infrastructure reporting system",
        "docs": "http://localhost:8000/docs",
        "health": "http://localhost:8000/health",
        "endpoints": {
            "POST /api/v1/analyze": "Upload image and generate report",
            "GET /api/v1/reports": "Retrieve all reports",
            "GET /api/v1/reports/{report_id}": "Retrieve single report",
            "PATCH /api/v1/reports/{report_id}": "Update report status",
        }
    }


# ============================================
# Route Registration
# ============================================

app.include_router(report_routes.router)
logger.info("Report routes registered")


# ============================================
# Application Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"Starting Uvicorn server on {host}:{port} (debug={debug})")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )
