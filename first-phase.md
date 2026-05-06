Key Improvements & Integrations:

1.  Backend Enhancements (FastAPI):
    - REST Endpoints: Implemented missing endpoints in main.py for /api/institutions, /api/profile,
      /api/sessions, and /api/sessions/{id}/report.
    - WebSocket Protocol: Aligned app/api/websocket.py with the frontend guide, moving to a
      binary-friendly audio protocol and standardizing message types (QUESTION, TRANSCRIPT, SESSION_END,
      etc.).
    - Session Management: Improved session creation and status tracking.

2.  Frontend Connectivity (SvelteKit):
    - Onboarding: Now fetches real institutions and positions from the backend and saves user preferences
      via the new /api/profile PATCH endpoint.
    - Dashboard: Replaced hardcoded stats and history with dynamic data from the user's profile and
      session history.
    - Real-time Interview:
      - Implemented full WebSocket communication logic.
      - Integrated Three.js with Draco decoding for the 3D avatar.
      - Added Audio Recording for real-time transcription (STT).
      - Connected Lip-Sync and Auto-Blink services to the live AI response stream.
    - History & Results: Created server-side loaders to fetch detailed session reports and a complete
      list of past sessions.

3.  Environment Configuration:
    - Created a .env file for the frontend to manage backend and WebSocket URLs.
    - Refactored lib/lipSync.ts to utilize these environment variables.

The application is now fully functional, moving from a static UI prototype to a connected system capable
of real-time AI-driven interview simulations.
