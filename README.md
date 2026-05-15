# CitySense — AI-Powered Civic Intelligence Platform for Smart Cities

CitySense is a full-stack AI-powered civic intelligence platform designed to modernize urban issue reporting and monitoring workflows. The platform enables citizens to report infrastructure and public safety issues in real time using a mobile application, while providing municipal authorities with an intelligent analytics dashboard for monitoring, prioritization, and decision-making.


---

## Key Features

### AI-Powered Civic Issue Detection

* Custom-trained YOLOv8 multi-class object detection pipeline for:

  * potholes
  * garbage accumulation
  * road damage
* Confidence-based detection filtering for improved reliability.
* Hybrid AI architecture combining Computer Vision + LLM reasoning.

### Grounded Multimodal AI Analysis

* Gemini Vision integration for:

  * contextual civic issue understanding
  * urgency estimation
  * municipal action recommendations
  * structured report generation
* Reduced hallucinations using YOLO-grounded inference before LLM reasoning.

### Realtime Civic Monitoring Dashboard

* Interactive web dashboard with:

  * live issue feed
  * geospatial map visualization
  * analytics charts
  * report monitoring tables
  * realtime Firestore updates

### Mobile Citizen Reporting Application

* Cross-platform React Native mobile app.
* Image capture and gallery upload support.
* GPS-enabled issue reporting.
* Realtime report submission to backend APIs.

### Scalable Backend Architecture

* FastAPI-based REST backend with modular service-oriented architecture.
* Structured Pydantic validation and AI response schemas.
* Firebase Firestore integration for realtime cloud persistence.
* Production-style AI processing pipeline with service abstraction.

---

## System Architecture

```text
        Mobile App 
            ↓
       FastAPI Backend
            ↓
     YOLOv8 Detection Layer
            ↓
  Gemini Grounded Reasoning
            ↓
 Firebase Firestore Storage
            ↓
  Realtime Monitoring Dashboard
```

---

## AI Pipeline

CitySense uses a multi-stage AI inference pipeline:

1. User uploads civic issue image.
2. YOLOv8 model performs object detection and issue localization.
3. Detection results are converted into structured context.
4. Gemini generates  civic analysis and recommendations.
5. Structured reports are stored in Firestore.
6. Dashboard updates in realtime for monitoring and analytics.

This hybrid architecture significantly improves consistency and reduces hallucinations compared to standalone LLM-based image analysis systems.



