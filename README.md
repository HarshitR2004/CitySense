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
  * map visualization
  * analytics charts
  * report monitoring tables
  * realtime Firestore updates

### Mobile Citizen Reporting Application

* Cross-platform React Native mobile app.
* Image capture and gallery upload support.
* GPS-enabled issue reporting.
* Realtime report submission to backend APIs.

---

## System Architecture

```text
        Mobile App 
            ↓
       FastAPI Backend
            ↓
 Firebase Storage + Firestore
      ↓
     Redis Queue
      ↓
    Celery Worker
      ↓
   YOLOv8 + Gemini Processing
      ↓
 Firebase Firestore Status Updates
      ↓
  Realtime Monitoring Dashboard
```
