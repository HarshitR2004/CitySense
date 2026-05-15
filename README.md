CitySense : An AI-powered civic intelligence and issue reporting platform for smart cities
========

Features
--------
- REST API backend for creating, querying, and managing reports (report creation, retrieval, listing).
- Firestore-backed data storage for reports and related metadata.
- LLM integration via for report summarization / classification.
- Web dashboard with interactive map, charts, and reports table for monitoring and analysis.
- Mobile app for capturing and submitting reports with photos and location data.
- Shared services and client utilities for Firebase integration and API calls.

Architecture
------------
- Monorepo with three main components:
  - `backend/`: Python REST API and service layer. Key modules include `routes/report_routes.py`, `services/report_service.py`, `services/firestore_service.py`, and `services/gemini_service.py`.
  - `dashboard/`: React + Vite single-page application. UI components (map, charts, reports table) live under `src/components/`; client helpers in `src/services/`.
  - `mobile-app/`: Expo React Native application (TypeScript). App-level components, screens, and services (location, gallery, API client) live under `app/` and `services/`.

- Data flow: Frontends (dashboard + mobile) call the backend REST API; the backend persists structured data to Firestore and delegates LLM work to the Gemini integration service.

