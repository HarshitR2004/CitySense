"""
Pydantic schemas for YOLOv8 detection output.

These models validate the structured visual grounding results that are passed
from the YOLO service into Gemini for grounded reasoning.
"""

from typing import List

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Pixel coordinates for a detected object."""

    x1: float = Field(..., description="Left coordinate")
    y1: float = Field(..., description="Top coordinate")
    x2: float = Field(..., description="Right coordinate")
    y2: float = Field(..., description="Bottom coordinate")


class YOLODetection(BaseModel):
    """Single high-confidence detection returned by YOLOv8."""

    class_name: str = Field(..., description="Detected object class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    bounding_box: BoundingBox = Field(..., description="Bounding box coordinates")


class YOLOAnalysisResponse(BaseModel):
    """Validated YOLO output used as grounding context for Gemini."""

    model_path: str = Field(..., description="Path to the loaded YOLO model")
    confidence_threshold: float = Field(..., description="Minimum confidence used for filtering")
    primary_issue_type: str = Field(..., description="Primary issue class derived from YOLO detections")
    detected_objects: List[YOLODetection] = Field(
        default_factory=list,
        description="High-confidence detections that survived filtering",
    )
