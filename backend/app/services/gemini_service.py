import json
import logging
import os
from typing import Any, Dict, Optional

import google.generativeai as genai
from pydantic import ValidationError

from app.models.report_schema import GeminiAnalysisResponse

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for grounded civic reasoning using Google Gemini."""

    def __init__(self):
        """Initialize Gemini service with API key from environment."""

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable not set")
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        genai.configure(api_key=api_key)

        self.model = genai.GenerativeModel(model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-3.1-flash-lite"))

        logger.info("Gemini service initialized with %s", os.getenv("GEMINI_MODEL_NAME", "gemini-3.1-flash-lite"))

    def analyze_image(self, image_bytes: Optional[bytes] = None, detection_context: Optional[Dict[str, Any]] = None) -> dict:
        """
        Generate a grounded municipal assessment using YOLO detections as the
        only visual evidence.
        """

        return self.analyze_detections(detection_context or {"detected_objects": [], "primary_issue_type": "other"})

    def analyze_detections(self, detection_context: Dict[str, Any]) -> dict:
        """Reason over YOLO detections and generate a structured civic report."""

        try:
            logger.info("Starting grounded Gemini reasoning using YOLO detections")

            prompt = self._build_grounded_prompt(detection_context)

            response = self.model.generate_content(
                [prompt],
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.2,
                    "top_p": 0.1,
                },
            )

            if not response.text:
                logger.error("Empty response from Gemini API")
                raise ValueError("Gemini API returned empty response")

            analysis_json = self._parse_gemini_response(
                response.text
            )

            logger.info("Grounded Gemini reasoning successful: %s", analysis_json.get("issueType"))

            return analysis_json

        except ValidationError as e:
            logger.error(f"Pydantic validation failed: {e}")
            raise ValueError("Invalid structured response from Gemini")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from Gemini: {e}")
            raise ValueError("Gemini returned invalid JSON")

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise

    async def analyze_detections_async(self, detection_context: Dict[str, Any]) -> dict:
        """Async wrapper for request offloading and background job compatibility."""

        import asyncio

        return await asyncio.to_thread(self.analyze_detections, detection_context)

    def _build_grounded_prompt(self, detection_context: Dict[str, Any]) -> str:
        """Build the prompt that grounds Gemini strictly on YOLO output."""

        detections_json = json.dumps(detection_context, indent=2, ensure_ascii=True)

        return f"""
You are a municipal civic analysis assistant.

You are provided with:

1. The uploaded image
2. Structured YOLOv8 detections that provide grounded visual cues

YOLO detections should be treated as strong guidance and primary grounding signals, especially for:

* potholes
* garbage accumulation
* road damage

However, you are still allowed to inspect the image holistically for additional visible civic issues that may not have been detected by YOLO.

Rules:

* Prioritize YOLO detections when they are confident and relevant.
* Do NOT ignore obvious visual evidence simply because YOLO missed it.
* Do NOT hallucinate hidden or speculative issues.
* Only report issues that are clearly visible in the image.
* If YOLO detections are weak or empty, fall back to cautious visual reasoning from the image.
* If uncertain, return:

  * issueType: "other"
  * urgency: "Low"

Task:

* identify the most relevant civic issue
* explain the likely public impact
* estimate urgency
* generate a concise municipal report description
* suggest the action a city team should take

Grounding context from YOLO:
{detections_json}

Required JSON schema:
{{
"issueType": "pothole | garbage_accumulation | road_damage | waterlogging | broken_infrastructure | other",
"description": "detailed issue description grounded in visible evidence",
"impact": "public impact assessment",
"suggestedAction": "recommended municipal action",
"urgency": "Low | Medium | High | Critical"
}}

Important:

* Use YOLO detections as grounding signals, not absolute constraints.
* Prefer consistency with YOLO when detections are strong.
* Avoid over-interpreting ambiguous scenes.
* Return only valid JSON.
  """


    def _parse_gemini_response(self, response_text: str) -> dict:
        """
        Parse and validate Gemini JSON response.
        """

        try:
            analysis_data = json.loads(response_text)

            # Validate using Pydantic schema
            validated_response = GeminiAnalysisResponse(
                **analysis_data
            )

            logger.info(
                "Gemini response parsed and validated successfully"
            )

            return validated_response.model_dump()

        except ValidationError as e:
            logger.error(f"Schema validation failed: {e}")
            raise

        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse Gemini response as JSON: {e}"
            )
            raise