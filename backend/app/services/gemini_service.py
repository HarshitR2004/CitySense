
import logging
import json
import os
from typing import Optional

import google.generativeai as genai

from app.models.report_schema import GeminiAnalysisResponse, IssueType, UrgencyLevel

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for analyzing images using Google Gemini Vision API."""

    def __init__(self):
        """Initialize Gemini service with API key from environment."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY environment variable not set")
            raise ValueError("GOOGLE_API_KEY environment variable is required")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-3.1-flash-lite")
        logger.info("Gemini service initialized with gemini-3.1-flash-lite")

    def analyze_image(self, image_bytes: bytes) -> dict:
        """
        Analyze an image using Gemini Vision API to detect civic infrastructure issues.

        Args:
            image_bytes: Image file content as bytes

        Returns:
            dict: Structured analysis response with keys:
                - issueType: Type of infrastructure issue
                - description: Detailed description
                - impact: Public safety impact
                - suggestedAction: Recommended municipal action
                - urgency: Urgency level (Low, Medium, High, Critical)

        Raises:
            ValueError: If image cannot be processed or API returns invalid response
            Exception: For API connectivity or rate limit issues
        """
        try:
            logger.info("Starting image analysis with Gemini Vision API")

            # Prepare the prompt for structured analysis
            analysis_prompt = """
Analyze this image for civic infrastructure issues. Focus on detecting:
- Potholes and road damage
- Garbage accumulation
- Waterlogging or flooding
- Broken or damaged infrastructure
- Public safety hazards

Respond ONLY with a valid JSON object (no markdown, no explanation) with these exact fields:
{
  "issueType": "one of: pothole, garbage_accumulation, road_damage, waterlogging, broken_infrastructure, other",
  "description": "detailed description of the issue observed",
  "impact": "assessment of public safety and urban impact",
  "suggestedAction": "recommended municipal action to address the issue",
  "urgency": "one of: Low, Medium, High, Critical"
}

If no infrastructure issue is detected, set urgency to "Low" and describe what was observed.
"""

            # Send image to Gemini with the structured prompt
            response = self.model.generate_content(
                [analysis_prompt, {"mime_type": "image/jpeg", "data": image_bytes}]
            )

            # Extract text response
            if not response.text:
                logger.error("Empty response from Gemini API")
                raise ValueError("Gemini API returned empty response")

            # Parse JSON response
            analysis_json = self._parse_gemini_response(response.text)
            logger.info(f"Image analysis successful: {analysis_json.get('issueType')}")

            return analysis_json

        except ValueError as e:
            logger.error(f"Invalid response from Gemini: {e}")
            raise
        except Exception as e:
            logger.error(f"Gemini API error during image analysis: {e}")
            raise

    def _parse_gemini_response(self, response_text: str) -> dict:
        """
        Parse and validate Gemini response text to extract structured JSON.

        Args:
            response_text: Raw text response from Gemini

        Returns:
            dict: Validated analysis dictionary

        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        try:
            # Try to find JSON in the response (may contain extra text)
            response_text = response_text.strip()

            # Remove markdown code block if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            # Parse JSON
            analysis_data = json.loads(response_text)

            # Validate required fields
            required_fields = {"issueType", "description", "impact", "suggestedAction", "urgency"}
            missing_fields = required_fields - set(analysis_data.keys())

            if missing_fields:
                raise ValueError(f"Missing required fields in response: {missing_fields}")

            # Validate field values
            valid_issue_types = {e.value for e in IssueType}
            if analysis_data["issueType"] not in valid_issue_types:
                logger.warning(f"Unknown issue type: {analysis_data['issueType']}, mapping to 'other'")
                analysis_data["issueType"] = "other"

            valid_urgencies = {e.value for e in UrgencyLevel}
            if analysis_data["urgency"] not in valid_urgencies:
                logger.warning(f"Unknown urgency level: {analysis_data['urgency']}, mapping to 'Medium'")
                analysis_data["urgency"] = "Medium"

            logger.info("Gemini response parsed and validated successfully")
            return analysis_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}\nResponse: {response_text}")
            raise ValueError(f"Invalid JSON in Gemini response: {e}")
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            raise ValueError(f"Error parsing Gemini response: {e}")
