"""
YOLOv8 inference service.

This service loads the trained model once, runs inference on uploaded images,
filters low-confidence detections, and returns a structured grounding context
for downstream Gemini reasoning.
"""

from __future__ import annotations

import asyncio
import logging
import os
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from PIL import Image
from ultralytics import YOLO

from app.models.yolo_schema import BoundingBox, YOLOAnalysisResponse, YOLODetection

logger = logging.getLogger(__name__)


class YOLOService:
    """Service for loading the trained YOLOv8 model and running inference."""

    def __init__(self, model_path: Optional[str] = None, confidence_threshold: Optional[float] = None):
        # Load the trained model once at startup so each request reuses the same
        # weights instead of reinitializing the detector.
        resolved_model_path = model_path or os.getenv("YOLO_MODEL_PATH")
        if resolved_model_path:
            self.model_path = Path(resolved_model_path)
        else:
            self.model_path = Path(__file__).resolve().parents[3] / "models" / "best_final.pt"

        self.confidence_threshold = confidence_threshold if confidence_threshold is not None else float(
            os.getenv("YOLO_CONFIDENCE_THRESHOLD", "0.5")
        )

        if not self.model_path.exists():
            logger.error("YOLO model file not found: %s", self.model_path)
            raise FileNotFoundError(f"YOLO model file not found: {self.model_path}")

        logger.info("Loading YOLOv8 model from %s", self.model_path)
        self.model = YOLO(str(self.model_path))
        logger.info("YOLOv8 model loaded successfully")

    def analyze_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Run YOLOv8 inference and return validated detections."""

        if not image_bytes:
            raise ValueError("Image bytes are required for YOLO inference")

        try:
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
        except Exception as exc:
            logger.error("Failed to decode image for YOLO inference: %s", exc)
            raise ValueError("Invalid image payload") from exc

        logger.info("Running YOLOv8 inference with confidence threshold %.2f", self.confidence_threshold)

        try:
            results = self.model.predict(source=image, conf=self.confidence_threshold, verbose=False)
        except Exception as exc:
            logger.error("YOLO inference failed: %s", exc, exc_info=True)
            raise

        if not results:
            logger.warning("YOLO returned no prediction results")
            return YOLOAnalysisResponse(
                model_path=str(self.model_path),
                confidence_threshold=self.confidence_threshold,
                primary_issue_type="other",
                detected_objects=[],
            ).model_dump()

        result = results[0]
        detections: List[YOLODetection] = []
        names = result.names or self.model.names or {}

        # Filter detections aggressively so Gemini only receives high-confidence
        # evidence that is likely to be meaningful for municipal reasoning.
        for box in result.boxes or []:
            confidence = float(box.conf[0]) if box.conf is not None else 0.0
            if confidence <= self.confidence_threshold:
                continue

            class_index = int(box.cls[0]) if box.cls is not None else -1
            if isinstance(names, dict):
                class_name = names.get(class_index, str(class_index))
            else:
                class_name = names[class_index] if 0 <= class_index < len(names) else str(class_index)

            x1, y1, x2, y2 = [float(value) for value in box.xyxy[0].tolist()]
            detections.append(
                YOLODetection(
                    class_name=class_name,
                    confidence=confidence,
                    bounding_box=BoundingBox(x1=x1, y1=y1, x2=x2, y2=y2),
                )
            )

        detections.sort(key=lambda detection: detection.confidence, reverse=True)
        primary_issue_type = detections[0].class_name if detections else "other"

        response = YOLOAnalysisResponse(
            model_path=str(self.model_path),
            confidence_threshold=self.confidence_threshold,
            primary_issue_type=primary_issue_type,
            detected_objects=detections,
        )

        logger.info(
            "YOLO inference complete: %s detection(s) above threshold, primary issue type=%s",
            len(detections),
            primary_issue_type,
        )
        return response.model_dump()

    async def analyze_image_async(self, image_bytes: bytes) -> Dict[str, Any]:
        """Async wrapper for future background processing and request offloading."""

        return await asyncio.to_thread(self.analyze_image, image_bytes)

    def build_gemini_context(self, yolo_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert validated YOLO output into a compact context payload for Gemini."""

        detected_objects: List[Dict[str, Any]] = []
        for detection in yolo_result.get("detected_objects", []):
            detected_objects.append(
                {
                    "class": detection["class_name"],
                    "confidence": detection["confidence"],
                    "bounding_box": detection["bounding_box"],
                }
            )

        return {
            "model_path": yolo_result.get("model_path", str(self.model_path)),
            "confidence_threshold": yolo_result.get("confidence_threshold", self.confidence_threshold),
            "primary_issue_type": yolo_result.get("primary_issue_type", "other"),
            "detected_objects": detected_objects,
        }
