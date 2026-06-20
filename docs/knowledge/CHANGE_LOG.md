# MedPredict Change Log

Every code or documentation change should add an entry here.

### 2026-06-20

Task:
Chatbot Groq API Integration

Files Modified:

- `backend/accounts/views.py`
- `backend/accounts/urls.py`
- `backend/accounts/tests.py`
- `frontend/src/components/ChatbotWindow.jsx`
- `docs/knowledge/AGENT_MEMORY.md`
- `docs/knowledge/CHANGE_LOG.md`

Reason:
Integrate the frontend chatbot window with the backend Groq Chat completions API, providing context-aware answers utilizing user information and conversation history.

Impact:
- Implemented `chatbot_message` POST endpoint in `accounts/views.py` using `openai/gpt-oss-120b` and a friendly assistant persona that addresses the user by their name and role.
- Registered `/api/accounts/chatbot/` url routing mapping.
- Wrote tests in `backend/accounts/tests.py` verifying chatbot authorization and payload requirements.
- Updated `ChatbotWindow.jsx` to call the new API dynamically, pass message history, and display a bouncy dots typing indicator during response generation.

Potential Risks:
- Direct dependency on Groq API limits. Handled gracefully with fallback responses if API times out.

### 2026-06-20

Task:
Groq API Integration & ai_service Removal

Files Modified:

- `docker-compose.yml`
- `backend/medpredict_api/settings.py`
- `backend/consultations/views.py`
- `backend/consultations/tests.py`
- `docs/knowledge/AGENT_MEMORY.md`
- `docs/knowledge/FILE_INDEX.md`
- `docs/knowledge/CHANGE_LOG.md`

Reason:
Migrate symptom prediction/analysis from a local Flask microservice to the external Groq Chat Completions API using the `GROQ_API_TOKEN` environment variable and the `openai/gpt-oss-120b` model.

Impact:
- Configured backend service in `docker-compose.yml` to load variables from `.env` containing `GROQ_API_TOKEN`.
- Discarded and stopped the local Flask `ai_service` container from the project.
- Updated the backend `analyze_symptoms` view to issue API calls to `https://api.groq.com/openai/v1/chat/completions` using the `openai/gpt-oss-120b` model and JSON mode, and to output the top 3 diseases based on requested symptoms.
- Refactored `backend/consultations/tests.py` unit tests to populate testing tokens and mock Groq API responses correctly.

Potential Risks:
- Direct dependency on Groq API service uptime and latency. Handled by fail-safe error handling.

### 2026-06-20

Task:
Patient Auto-Account & Appointment Tracking Portal

Files Modified:

- `backend/accounts/models.py`
- `backend/patients/models.py`
- `backend/appointments/views.py`
- `backend/appointments/urls.py`
- `backend/appointments/tests.py`
- `backend/accounts/permissions.py`
- `frontend/src/pages/PatientPortal.jsx` (new)
- `frontend/src/pages/Login.jsx`
- `frontend/src/pages/PublicBooking.jsx`
- `frontend/src/components/ProtectedRoute.jsx`
- `frontend/src/App.jsx`
- `docs/knowledge/AGENT_MEMORY.md`
- `docs/knowledge/CHANGE_LOG.md`

Reason:
Provide auto-account creation for patients during public booking, and a beautiful space (Patient Portal) for them to check and track their appointments.

Impact:
- Added `PATIENT` role to User model.
- Added nullable `user` OneToOneField to `Patient` model.
- Updated public booking endpoint to automatically create patient user accounts using `username=CIN` and `password=CIN+"2025"`.
- Created patient appointments API endpoint `/api/appointments/my/` for the logged-in patient.
- Upgraded permissions in `accounts/permissions.py` to prevent `PATIENT` users from accessing staff endpoints.
- Created `PatientPortal.jsx` with visual branding, upcoming/past lists, and logout functionality.
- Configured client-side routing in `App.jsx` and `ProtectedRoute.jsx` to isolate patient pages and redirect role mismatches.
- Updated `Login.jsx` to redirect `PATIENT` role to the patient portal.
- Updated `PublicBooking.jsx` to display credentials or existing account notifications upon booking completion.
- Implemented Django unit tests covering the new functionality.

Potential Risks:
- Guessable default password pattern (CIN + "2025"). Suitable for demo purposes.

### 2026-06-20

Task:
Upgrade SECRETARY role from blanket read-only to proper clinic secretary capabilities.

Files Modified:

- `backend/accounts/permissions.py`
- `backend/patients/views.py`
- `backend/appointments/views.py`
- `backend/consultations/views.py`
- `backend/prescriptions/views.py`
- `frontend/src/pages/Patients.jsx`
- `backend/seed_data.py`
- `docs/knowledge/AGENT_MEMORY.md`
- `docs/knowledge/CHANGE_LOG.md`

Reason:
The SECRETARY role was a blanket read-only viewer everywhere via `IsSecretaryReadOnly`, which doesn't match real clinic workflows. Secretaries need to register patients and manage the appointment schedule.

Impact:
- Replaced single `IsSecretaryReadOnly` permission with three granular classes: `IsAdminOrDoctorOrSecretary`, `IsDoctorOrAdmin`, and `IsSecretaryReadOnly`.
- Secretaries can now create/edit patients and fully manage appointments (create, edit, confirm, cancel, delete).
- Consultations are fully blocked for secretaries (medical acts — `IsDoctorOrAdmin`).
- Prescriptions remain read-only with PDF download for secretaries.
- Added `IsSecretaryReadOnly` to `PrescriptionViewSet` which previously had no permission class at all.
- Frontend hides patient delete button for secretaries.
- Added secretary seed user `sec_alami` / `password123` for testing.

Potential Risks:
- Patient delete is only hidden in frontend for secretaries, not blocked at backend level. Acceptable since secretaries don't have delete buttons visible.
- Prescriptions ViewSet previously had no permission class — adding `IsSecretaryReadOnly` now enforces authentication for all prescription operations.

### 2026-06-19

Task:
Add perfect dark mode with theme toggle and CSS variables.

Files Modified:

- `frontend/src/index.css`
- `frontend/src/store/useThemeStore.js` (new)
- `frontend/src/components/ThemeToggle.jsx` (new)
- `frontend/src/App.jsx`
- `frontend/src/components/Layout.jsx`
- `frontend/src/components/ChatbotWindow.jsx`
- `frontend/src/components/ChatbotButton.jsx`
- `frontend/src/pages/Login.jsx`
- `frontend/src/pages/Dashboard.jsx`
- `docs/DARK_MODE_GUIDE.md` (new)
- `docs/knowledge/AGENT_MEMORY.md`

Reason:
Implement a complete dark mode system using CSS variables and Zustand state management. All UI components now support seamless light/dark theme switching with persisted user preference.

Impact:
- Users can toggle between light and dark modes via the Moon/Sun icon in the topbar
- Theme preference is saved to localStorage and restored on page refresh
- All components (Layout, Chatbot, Charts, Forms, Pages) are theme-aware
- CSS variables adjust 40+ color properties for consistent theme switching
- Dashboard charts dynamically adjust colors based on theme
- Zero visual "flash" on page load - theme initializes before render

Potential Risks:
- Components with hardcoded colors will not adapt (all found and fixed in this update)
- Future components must use CSS variables for full theme support
- localStorage dependency (disabled in private browsing may cause issues)

### 2026-06-19

Task:
Add functional chatbot floating button with open/close window.

Files Modified:

- `frontend/src/components/ChatbotButton.jsx` (new)
- `frontend/src/components/ChatbotWindow.jsx` (new)
- `frontend/src/store/useChatbotStore.js` (new)
- `frontend/src/components/Layout.jsx`
- `frontend/src/index.css`
- `docker-compose.yml`
- `docs/knowledge/FILE_INDEX.md`
- `docs/knowledge/CHANGE_LOG.md`

Reason:
Add a floating chatbot UI component to the clinic dashboard that allows users to open/close a conversation window. The feature includes state management via Zustand, smooth animations, and simulated bot responses.

Impact:
- Users now see a floating blue message button in the bottom-right corner of authenticated pages.
- Clicking toggles a chat window with message history, timestamps, and input field.
- The chatbot currently provides simulated responses; ready for backend AI service integration.
- All chatbot state is managed in a dedicated Zustand store for future extensibility.

Potential Risks:
- None identified. Chatbot is isolated to protected pages via Layout and does not affect existing functionality.
- Backend AI endpoint integration is not yet implemented (currently client-side simulation).

### 2026-06-19

Task:
Fix database startup failure by disabling init_db.sql mount.

Files Modified:

- `docker-compose.yml`

Reason:
The `init_db.sql` file is UTF-16 little-endian encoded with destructive DROP statements that caused the Postgres container to crash on startup. The file attempted to drop non-existent tables, preventing successful initialization.

Impact:
Database now initializes cleanly via Django migrations instead of pre-existing SQL dump. All services start without errors.

Potential Risks:
If the `init_db.sql` content is needed in the future, it should be converted to UTF-8 and validated to ensure all tables exist before dropping.

### 2026-06-19

Task:
Fix backend Docker build failure caused by corrupted Twilio requirement.

Files Modified:

- `backend/requirements.txt`
- `docs/knowledge/PROJECT_OVERVIEW.md`
- `docs/knowledge/FILE_INDEX.md`
- `docs/knowledge/CHANGE_LOG.md`
- `docs/knowledge/AGENT_MEMORY.md`

Reason:
`pip install -r requirements.txt` failed during the backend Docker build because the `twilio==9.10.9` line contained embedded null bytes and was parsed as an invalid requirement.

Impact:
The backend requirements file is now plain ASCII text and Docker can install backend dependencies successfully.

Potential Risks:
No functional dependency changes were intended; the file content is the same dependency set with corrected encoding.

### 2026-06-19

Task:
Add Makefile for project startup, dependency services, database setup, seeding, and AI training.

Files Modified:

- `Makefile`
- `docs/knowledge/PROJECT_OVERVIEW.md`
- `docs/knowledge/FILE_INDEX.md`
- `docs/knowledge/CHANGE_LOG.md`
- `docs/knowledge/AGENT_MEMORY.md`

Reason:
Provide a single command path to build and run the full Docker Compose stack, apply migrations, create an admin account, load demo data, and train the AI model.

Impact:
Developers can run `make setup` for full local bootstrap and use smaller targets such as `make up`, `make migrate`, `make seed`, `make train-ai`, `make logs`, and `make down`.

Potential Risks:
`make seed` runs `backend/seed_data.py`, which clears existing non-superuser domain/demo data before inserting demo records.

### 2026-06-19

Task:
Bootstrap persistent repository knowledge base.

Files Modified:

- `docs/knowledge/PROJECT_OVERVIEW.md`
- `docs/knowledge/ARCHITECTURE.md`
- `docs/knowledge/FILE_INDEX.md`
- `docs/knowledge/CHANGE_LOG.md`
- `docs/knowledge/AGENT_MEMORY.md`
- `docs/knowledge/MISTAKES.md`

Reason:
Create durable codebase understanding so future agents can work without rereading the full repository.

Impact:
Documents system purpose, architecture, core workflows, important files, data flow, API flow, operational notes, and known pitfalls.

Potential Risks:
Docs may become stale if future code changes are not reflected here. Future tasks must update this change log and relevant knowledge files.
