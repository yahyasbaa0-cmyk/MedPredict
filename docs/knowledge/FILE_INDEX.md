# MedPredict File Index

This index covers important source, configuration, deployment, data, and documentation files. Empty package marker files and trivial generated files are grouped where useful.

## Root

#### `README.md`

Purpose:
French project overview and quick-start guide.

Responsibilities:

- Explains MedPredict purpose and stack.
- Documents Docker Compose startup.
- Gives demo workflow and future improvement ideas.

Dependencies:

- `docker-compose.yml`
- `backend/`
- `frontend/`
- `ai_service/`

Used By:

- Developers and evaluators starting the project.

Important Notes:

- Mentions Swagger at `http://localhost:8000/swagger/`.
- Says to train the AI model with `docker-compose exec ai_service python model/train.py`.

#### `docker-compose.yml`

Purpose:
Defines local multi-service runtime.

Responsibilities:

- Starts Postgres, Django backend, Vite frontend, and Flask AI service.
- Wires `AI_SERVICE_URL` to the Docker service name.
- Mounts source directories as volumes for development.

Dependencies:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `ai_service/Dockerfile`
- `init_db.sql`

Used By:

- Local Docker startup.

Important Notes:

- Frontend command overrides Vite config and runs on port 5173.
- Backend depends on `db`, but not on `ai_service`.

#### `Makefile`

Purpose:
Local developer command surface for running the full project and common maintenance tasks.

Responsibilities:

- Builds and starts Docker Compose services.
- Waits for Postgres readiness before migrations.
- Applies migrations.
- Creates a default admin user if missing.
- Seeds demo data through `backend/seed_data.py`.
- Trains AI artifacts through `ai_service/model/train.py`.
- Provides helper targets for logs, status, tests, shells, shutdown, and volume cleanup.

Dependencies:

- Docker Compose.
- `docker-compose.yml`
- `backend/seed_data.py`
- `ai_service/model/train.py`

Used By:

- Developers bootstrapping or operating the local project.

Important Notes:

- `make setup` is the one-command path for full local startup.
- `make seed` uses `backend/seed_data.py`, which deletes existing non-superuser demo/domain data before recreating demo records.
- Admin defaults can be overridden with `ADMIN_USERNAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD`.

#### `init_db.sql`

Purpose:
PostgreSQL initialization dump mounted into the database container.

Responsibilities:

- Intended to restore database objects/data on first Postgres volume initialization.

Dependencies:

- PostgreSQL Docker entrypoint.

Used By:

- `docker-compose.yml` `db` service.

Important Notes:

- File is UTF-16 little-endian with CRLF terminators.
- Contains destructive dump content such as `DROP TABLE` before `CREATE TABLE`.

#### `start.ps1`

Purpose:
Windows PowerShell startup helper.

Responsibilities:

- Builds and starts Docker containers.
- Runs migrations.
- Creates an `admin` superuser if missing.
- Trains the AI model.
- Prints service URLs.

Dependencies:

- Docker Compose.
- Backend and AI containers.

Used By:

- Windows users wanting one-command setup.

Important Notes:

- Creates `admin` / `admin@example.com` / `admin`.

#### `start_ngrok.bat`

Purpose:
Tunnel helper for exposing backend to Twilio.

Responsibilities:

- Runs `cloudflared.exe tunnel --url http://localhost:8000`.

Dependencies:

- Local `cloudflared.exe`.

Used By:

- WhatsApp webhook setup.

Important Notes:

- Filename says ngrok but command uses Cloudflare Tunnel.

#### `test_whatsapp.py`

Purpose:
Manual WhatsApp webhook test script.

Responsibilities:

- Posts a sequence of form messages to the local WhatsApp webhook.

Dependencies:

- `requests`
- Running backend at `localhost:8000`.

Used By:

- Developers testing the Twilio state machine without Twilio.

Important Notes:

- Uses phone `whatsapp:+212600000000`.

#### `LISEZ_MOI.txt`

Purpose:
French end-user installation guide.

Responsibilities:

- Gives Docker Desktop setup instructions.
- Lists local service URLs.
- Lists demo login emails/passwords.

Dependencies:

- Docker Compose.

Used By:

- Non-technical setup/readme flow.

Important Notes:

- Credentials listed here may depend on restored database contents.

#### `tunnel.txt` and `pinggy.txt`

Purpose:
Tunnel-related notes or generated tunnel output.

Responsibilities:

- Not part of core application logic.

Dependencies:

- External tunnel tooling.

Used By:

- Manual webhook exposure workflows.

Important Notes:

- Review before relying on them; contents were not part of the main architecture.

## Backend Project

#### `backend/manage.py`

Purpose:
Django management entrypoint.

Responsibilities:

- Sets `DJANGO_SETTINGS_MODULE=medpredict_api.settings`.
- Runs management commands.

Dependencies:

- `backend/medpredict_api/settings.py`

Used By:

- Migrations, runserver, tests, shell, seed scripts.

Important Notes:

- Primary backend CLI entrypoint.

#### `backend/requirements.txt`

Purpose:
Python dependency list for the Django backend.

Responsibilities:

- Installs Django, DRF, JWT, Postgres adapter, CORS, Swagger, ReportLab, requests, dotenv, django-filter, and Twilio.

Dependencies:

- `backend/Dockerfile`

Used By:

- Backend Docker build and local Python installs.

Important Notes:

- This file was normalized to plain ASCII/UTF-8 on 2026-06-19 after a corrupted UTF-16/null-byte Twilio line broke Docker builds.

#### `backend/Dockerfile`

Purpose:
Backend container image definition.

Responsibilities:

- Uses Python 3.11 slim.
- Installs gcc/libpq-dev for Postgres dependencies.
- Installs Python requirements.
- Copies backend source into `/app`.

Dependencies:

- `backend/requirements.txt`

Used By:

- `docker-compose.yml` backend service.

Important Notes:

- Runtime command is defined in Compose, not Dockerfile.

#### `backend/medpredict_api/settings.py`

Purpose:
Django project settings.

Responsibilities:

- Configures installed apps, middleware, auth model, database selection, REST auth, CORS, JWT lifetimes, AI service URL, and unused Celery settings.

Dependencies:

- Environment variables for Postgres and AI service.
- Django apps under `backend/`.

Used By:

- Entire Django runtime.

Important Notes:

- Uses SQLite when `POSTGRES_HOST` is absent.
- `DEBUG=True`, wildcard hosts, and all-origin CORS are development settings.

#### `backend/medpredict_api/urls.py`

Purpose:
Root API route map.

Responsibilities:

- Mounts app URL modules under `/api/...`.
- Exposes Django admin, Swagger, and ReDoc.

Dependencies:

- `accounts.urls`
- `patients.urls`
- `appointments.urls`
- `consultations.urls`
- `prescriptions.urls`
- `dashboard.urls`

Used By:

- Django URL resolver.

Important Notes:

- Swagger is public via `AllowAny`.

#### `backend/medpredict_api/asgi.py` and `backend/medpredict_api/wsgi.py`

Purpose:
ASGI/WSGI server entrypoints.

Responsibilities:

- Set settings module and expose application object.

Dependencies:

- `medpredict_api.settings`

Used By:

- Deployment servers if used outside dev runserver.

Important Notes:

- Compose currently uses `python manage.py runserver`, not these directly.

## Backend Accounts App

#### `backend/accounts/models.py`

Purpose:
Custom user and notification models.

Responsibilities:

- Extends `AbstractUser` with `role` and `phone`.
- Defines role choices `ADMIN`, `DOCTOR`, `SECRETARY`.
- Defines notification recipient/message/read flag/timestamp.

Dependencies:

- Django auth models.

Used By:

- Auth, permissions, appointment notifications, dashboard doctor counts.

Important Notes:

- `AUTH_USER_MODEL` points here.

#### `backend/accounts/serializers.py`

Purpose:
DRF serializers for users, notifications, and JWT custom claims.

Responsibilities:

- Serializes public user fields.
- Serializes notification fields.
- Adds role/email/name claims to JWT access token.

Dependencies:

- SimpleJWT `TokenObtainPairSerializer`.

Used By:

- `accounts.views`
- `accounts.urls`
- Frontend auth store.

Important Notes:

- Frontend decodes access token payload instead of calling `/me`.

#### `backend/accounts/views.py`

Purpose:
Accounts and notifications API.

Responsibilities:

- Provides `UserViewSet`.
- Restricts user create/delete to admins.
- Provides per-recipient `NotificationViewSet`.
- Implements `mark_all_read` action.

Dependencies:

- `accounts.models`
- `accounts.serializers`

Used By:

- Frontend appointment page doctor list.
- Layout notification dropdown.

Important Notes:

- Non-admin authenticated users can list users.

#### `backend/accounts/urls.py`

Purpose:
Accounts route map.

Responsibilities:

- Registers `users` and `notifications` routers.
- Provides JWT login and refresh endpoints.

Dependencies:

- `CustomTokenObtainPairSerializer`

Used By:

- Root URL config.

Important Notes:

- Login path is `/api/auth/login/`.

#### `backend/accounts/admin.py`

Purpose:
Django admin integration for custom user.

Responsibilities:

- Adds role and phone to admin fieldsets.

Dependencies:

- `accounts.models.User`

Used By:

- Django admin.

Important Notes:

- `Notification` is not explicitly registered.

#### `backend/accounts/migrations/*.py`

Purpose:
Database migrations for custom user and notifications.

Responsibilities:

- Create custom user.
- Adjust role choices over time.
- Add notification table.

Dependencies:

- Django migration framework.

Used By:

- `manage.py migrate`.

Important Notes:

- Role previously included `PATIENT` then returned to staff-only roles.

## Backend Patients App

#### `backend/patients/models.py`

Purpose:
Patient domain model.

Responsibilities:

- Stores identity, contact, city, medical history, allergies, blood group, emergency contact, archive flag, and creator.
- Validates Moroccan phone formats.

Dependencies:

- `accounts.User` via string FK.

Used By:

- Patient CRUD, appointments, dashboard, public booking, WhatsApp booking.

Important Notes:

- `cin` is unique but nullable/blank.

#### `backend/patients/serializers.py`

Purpose:
Patient serializer.

Responsibilities:

- Exposes all patient model fields.

Dependencies:

- `patients.models.Patient`

Used By:

- `PatientViewSet`
- Nested appointment serializer.

Important Notes:

- No field-level write restrictions are enforced here.

#### `backend/patients/views.py`

Purpose:
Patient CRUD API.

Responsibilities:

- Enables search, ordering, and `is_archived` filtering.
- Scopes doctor queryset to relevant or created patients.
- Sets `created_by` during create.

Dependencies:

- Django filters.
- `patients.models.Patient`

Used By:

- Frontend patients and appointments pages.

Important Notes:

- Search covers first name, last name, phone, and email.

#### `backend/patients/urls.py`

Purpose:
Patient route map.

Responsibilities:

- Registers `PatientViewSet` at `/api/patients/`.

Dependencies:

- `patients.views.PatientViewSet`

Used By:

- Root URL config.

Important Notes:

- Empty router prefix means detail routes are `/api/patients/{id}/`.

#### `backend/patients/migrations/*.py`

Purpose:
Patient schema history.

Responsibilities:

- Create patient table.
- Add CIN, city, phone regex, emergency contact, creator.
- Add and remove an older one-to-one user profile link.

Dependencies:

- Django migration framework.

Used By:

- `manage.py migrate`.

Important Notes:

- Current model no longer has patient user accounts.

## Backend Appointments App

#### `backend/appointments/models.py`

Purpose:
Appointment and WhatsApp session models.

Responsibilities:

- Stores appointment patient, doctor, date/time, duration, reason, status, timestamps.
- Validates double booking and daily capacity.
- Stores WhatsApp conversation state by phone number.

Dependencies:

- `patients.Patient`
- `accounts.User`

Used By:

- Appointment CRUD, public booking, WhatsApp webhook, consultations.

Important Notes:

- Validation only checks exact time equality, not duration overlap.
- Daily cap is 8 non-cancelled appointments per doctor.

#### `backend/appointments/serializers.py`

Purpose:
Appointment serializer.

Responsibilities:

- Exposes all appointment fields.
- Adds nested read-only `patient_details` and `doctor_details`.

Dependencies:

- Patient and user serializers.

Used By:

- Appointment viewset.
- Nested consultation serializer.

Important Notes:

- Write payloads still use `patient` and `doctor` IDs.

#### `backend/appointments/views.py`

Purpose:
Appointment API and public booking endpoints.

Responsibilities:

- Provides authenticated appointment CRUD.
- Scopes doctors to their own appointments.
- Creates notifications on appointment creation.
- Provides public doctors list, available slots, and public booking.

Dependencies:

- `Appointment`, `Patient`, `User`, `Notification`

Used By:

- Frontend appointment page.
- Public booking page.

Important Notes:

- Public booking defaults `date_of_birth` to `2000-01-01` when omitted.
- Available slots are a hardcoded list of 8 times.

#### `backend/appointments/whatsapp_views.py`

Purpose:
Twilio WhatsApp webhook.

Responsibilities:

- Parses incoming messages.
- Maintains state in `WhatsAppSession`.
- Creates patients and appointments from chat flow.
- Responds with TwiML XML.

Dependencies:

- `twilio.twiml.messaging_response.MessagingResponse`
- `WhatsAppSession`, `Appointment`, `Patient`, `User`

Used By:

- Twilio or manual `test_whatsapp.py`.

Important Notes:

- Doctor choices are hardcoded to usernames `dr_bennani` and `dr_chaoui`.
- Uses default birth date `1990-01-01` and gender `O` for new WhatsApp patients.

#### `backend/appointments/urls.py`

Purpose:
Appointment route map.

Responsibilities:

- Registers appointment viewset.
- Exposes public booking and WhatsApp webhook routes.

Dependencies:

- `appointments.views`
- `appointments.whatsapp_views`

Used By:

- Root URL config.

Important Notes:

- Public routes appear before router include.

#### `backend/appointments/migrations/*.py`

Purpose:
Appointment schema history.

Responsibilities:

- Create appointments table.
- Add WhatsApp session table.
- Increase WhatsApp phone number length.

Dependencies:

- Patient and user migrations.

Used By:

- `manage.py migrate`.

Important Notes:

- WhatsApp phone number is the primary key.

## Backend Consultations App

#### `backend/consultations/models.py`

Purpose:
Consultation domain model.

Responsibilities:

- Links one consultation to one appointment.
- Stores symptoms, examination, diagnosis, doctor notes, and AI suggestions.

Dependencies:

- `appointments.Appointment`

Used By:

- Consultation API, dashboard, prescriptions.

Important Notes:

- `ai_suggestions` is JSON and optional.

#### `backend/consultations/serializers.py`

Purpose:
Consultation serializer.

Responsibilities:

- Exposes all consultation fields.
- Adds nested read-only appointment details.

Dependencies:

- `appointments.serializers.AppointmentSerializer`

Used By:

- Consultation viewset.

Important Notes:

- Write payload uses `appointment` ID.

#### `backend/consultations/views.py`

Purpose:
Consultation CRUD and AI proxy API.

Responsibilities:

- Scopes doctors to their own consultations.
- Blocks secretary mutation methods.
- Calls AI service for symptom analysis.
- Returns fail-safe response when AI service is unavailable.

Dependencies:

- `requests`
- `settings.AI_SERVICE_URL`

Used By:

- Frontend consultation page.

Important Notes:

- AI request timeout is 2 seconds.

#### `backend/consultations/urls.py`

Purpose:
Consultation route map.

Responsibilities:

- Registers `ConsultationViewSet` at `/api/consultations/`.

Dependencies:

- `consultations.views.ConsultationViewSet`

Used By:

- Root URL config.

Important Notes:

- Custom action path is `/api/consultations/analyze-symptoms/`.

#### `backend/consultations/tests.py`

Purpose:
AI proxy integration tests.

Responsibilities:

- Tests successful AI response via mocked `requests.post`.
- Tests service-down fail-safe via mocked connection error.

Dependencies:

- DRF test client.
- `accounts.User`

Used By:

- Backend test suite.

Important Notes:

- Test mock success uses `probability`, while real AI returns `confidence`.

#### `backend/consultations/migrations/*.py`

Purpose:
Consultation schema.

Responsibilities:

- Creates consultation table with one-to-one appointment relation.

Dependencies:

- Appointment migration.

Used By:

- `manage.py migrate`.

Important Notes:

- One consultation per appointment is enforced.

## Backend Prescriptions App

#### `backend/prescriptions/models.py`

Purpose:
Prescription domain model.

Responsibilities:

- Links prescriptions to consultations.
- Stores medications, dosage, posology, duration, recommendations, timestamp.

Dependencies:

- `consultations.Consultation`

Used By:

- Prescription API and PDF export.

Important Notes:

- Current relationship is many prescriptions per consultation.

#### `backend/prescriptions/serializers.py`

Purpose:
Prescription serializer.

Responsibilities:

- Exposes all prescription fields.
- Adds nested read-only consultation details.

Dependencies:

- `consultations.serializers.ConsultationSerializer`

Used By:

- Prescription viewset.

Important Notes:

- Write payload uses `consultation` ID.

#### `backend/prescriptions/views.py`

Purpose:
Prescription CRUD and PDF export.

Responsibilities:

- Scopes doctors to prescriptions for their consultations.
- Generates ReportLab PDF for a prescription.

Dependencies:

- ReportLab.
- `PrescriptionSerializer`

Used By:

- Frontend prescription page.

Important Notes:

- PDF uses bullet character in text lines; this file already contains non-ASCII French text.

#### `backend/prescriptions/urls.py`

Purpose:
Prescription route map.

Responsibilities:

- Registers `PrescriptionViewSet`.

Dependencies:

- `prescriptions.views.PrescriptionViewSet`

Used By:

- Root URL config.

Important Notes:

- PDF endpoint is `/api/prescriptions/{id}/export-pdf/`.

#### `backend/prescriptions/migrations/*.py`

Purpose:
Prescription schema history.

Responsibilities:

- Create prescription table.
- Change consultation relation from one-to-one to foreign key.

Dependencies:

- Consultation migration.

Used By:

- `manage.py migrate`.

Important Notes:

- Current app allows multiple prescriptions per consultation.

## Backend Dashboard App

#### `backend/dashboard/views.py`

Purpose:
Dashboard statistics endpoint.

Responsibilities:

- Counts patients, doctors, recent consultations, appointment statuses, top diagnoses, and AI usage.

Dependencies:

- `Patient`, `Appointment`, `Consultation`, `User`

Used By:

- Frontend dashboard page.

Important Notes:

- No doctor-specific scoping; all authenticated users receive global stats.

#### `backend/dashboard/urls.py`

Purpose:
Dashboard route map.

Responsibilities:

- Exposes `GET /api/dashboard/stats/`.

Dependencies:

- `DashboardStatsView`

Used By:

- Root URL config.

Important Notes:

- Requires authentication.

#### `backend/dashboard/models.py`

Purpose:
Placeholder app models file.

Responsibilities:

- No domain models currently.

Dependencies:

- None.

Used By:

- Django app structure.

Important Notes:

- Dashboard is read-only aggregation over other apps.

## Backend Seed And Test Helpers

#### `backend/seed_data.py`

Purpose:
Primary demo data seeding script.

Responsibilities:

- Deletes non-superuser demo data.
- Creates doctors, patients, appointments, one consultation, and one prescription.

Dependencies:

- Django settings and domain models.

Used By:

- Manual demo setup.

Important Notes:

- Doctor usernames match WhatsApp hardcoded choices.

#### `backend/seed_more.py`

Purpose:
Bulk demo data script.

Responsibilities:

- Creates additional randomized patients, appointments, and consultations.

Dependencies:

- Domain models.

Used By:

- Manual demo enrichment.

Important Notes:

- The visible file contents appear malformed/truncated around CIN generation; inspect before running.

#### `backend/seed_data_extra.py`

Purpose:
Additional demo data generator.

Responsibilities:

- Creates randomized Moroccan patient profiles, appointments, consultations, and some prescriptions.

Dependencies:

- Domain models.

Used By:

- Manual demo enrichment.

Important Notes:

- Catches and skips appointment validation collisions.

#### `backend/*/admin.py`, `backend/*/apps.py`, `backend/*/tests.py`

Purpose:
Standard Django app support files.

Responsibilities:

- Register models/admin behavior when present.
- Define app configs.
- Hold placeholder tests except `consultations/tests.py`.

Dependencies:

- Django app framework.

Used By:

- Django runtime and test discovery.

Important Notes:

- Most tests are placeholders with only generated comments.

## AI Service (Deprecated/Obsolete - Replaced by Groq API Integration on 2026-06-20)

#### `ai_service/app.py`

Purpose:
Flask prediction API.

Responsibilities:

- Loads trained model and feature list from `ai_service/model`.
- Exposes `GET /health`.
- Exposes `POST /predict` accepting `{"symptoms": [...]}`.
- Builds binary feature vector and returns top 3 disease predictions.

Dependencies:

- `joblib`, `pandas`, Flask, Flask-CORS.
- `ai_service/model/model.pkl`
- `ai_service/model/features.joblib`

Used By:

- Backend consultation AI proxy.

Important Notes:

- If model artifacts are missing, `/predict` returns 500.

#### `ai_service/model/train.py`

Purpose:
Model training script.

Responsibilities:

- Reads `dataset.csv`.
- Trains a RandomForest classifier.
- Writes `model.pkl` and `features.joblib`.

Dependencies:

- pandas, scikit-learn, joblib.
- `ai_service/model/dataset.csv`

Used By:

- Manual setup and `start.ps1`.

Important Notes:

- Features are all CSV columns except `disease`.

#### `ai_service/model/dataset.csv`

Purpose:
Training dataset.

Responsibilities:

- Provides symptom feature columns and disease target.

Dependencies:

- `train.py`

Used By:

- AI model training.

Important Notes:

- Symptom names must match frontend/backend symptom strings to affect prediction.

#### `ai_service/model/model.pkl` and `ai_service/model/features.joblib`

Purpose:
Trained AI artifacts.

Responsibilities:

- Store fitted classifier and feature column order/names.

Dependencies:

- Produced by `train.py`.

Used By:

- `ai_service/app.py`

Important Notes:

- Re-train after changing `dataset.csv`.

#### `ai_service/requirements.txt`

Purpose:
AI service Python dependencies.

Responsibilities:

- Installs Flask, scikit-learn, pandas, numpy, joblib, Flask-CORS.

Dependencies:

- `ai_service/Dockerfile`

Used By:

- AI Docker build.

Important Notes:

- Pins specific package versions.

#### `ai_service/Dockerfile`

Purpose:
AI service container image definition.

Responsibilities:

- Uses Python 3.11 slim.
- Installs AI requirements.
- Copies AI service code into `/app`.

Dependencies:

- `ai_service/requirements.txt`

Used By:

- `docker-compose.yml` AI service.

Important Notes:

- Runtime command is defined in Compose.

## Frontend Core

#### `frontend/package.json`

Purpose:
Frontend package manifest.

Responsibilities:

- Defines dev/build/lint/preview scripts.
- Lists React, router, Zustand, Axios, charts, icons, FullCalendar, Tailwind, Vite, ESLint dependencies.

Dependencies:

- npm.

Used By:

- Local frontend and Docker build.

Important Notes:

- React 19 and React Router 7 are used.

#### `frontend/vite.config.js`

Purpose:
Vite configuration.

Responsibilities:

- Registers React plugin.
- Configures dev server port 9654, strict port, polling, HMR client port.

Dependencies:

- Vite.

Used By:

- `npm run dev`, unless Compose command overrides server args.

Important Notes:

- Docker Compose runs Vite on port 5173 despite this file.

#### `frontend/src/main.jsx`

Purpose:
React app entrypoint.

Responsibilities:

- Renders `App` into `#root` inside `StrictMode`.

Dependencies:

- `frontend/src/App.jsx`
- `frontend/src/index.css`

Used By:

- Vite.

Important Notes:

- Main frontend execution entrypoint.

#### `frontend/src/App.jsx`

Purpose:
Frontend route map.

Responsibilities:

- Defines login and public booking routes.
- Wraps authenticated app routes in `ProtectedRoute` and `Layout`.
- Applies role guards to consultations and prescriptions.
- Mounts `ToastProvider`.

Dependencies:

- React Router.
- Pages and components.

Used By:

- `main.jsx`

Important Notes:

- Unauthorized role redirect points to `/unauthorized`, which has no explicit route and will fall back to `/`.

#### `frontend/src/services/api.js`

Purpose:
Authenticated Axios API client.

Responsibilities:

- Sets API base URL.
- Adds JWT bearer token from `localStorage`.
- Clears auth keys and redirects to `/login` on 401.

Dependencies:

- Axios.
- `VITE_API_BASE_URL`.

Used By:

- Auth store, layout, protected pages.

Important Notes:

- Public booking does not use this client; it hardcodes `http://localhost:8000/api`.

#### `frontend/src/store/useAuthStore.js`

Purpose:
Persistent authentication store.

Responsibilities:

- Logs in through `/auth/login/`.
- Decodes JWT payload manually.
- Stores token and user in Zustand persist.
- Writes/removes `medpredict_token` in `localStorage`.

Dependencies:

- Zustand persist middleware.
- Axios API client.

Used By:

- Login, layout, protected routes, consultations.

Important Notes:

- Also creates persisted storage key `medpredict-auth-storage`.

#### `frontend/src/store/useToastStore.js`

Purpose:
Toast notification state.

Responsibilities:

- Adds/removes toast messages.
- Auto-removes toasts after a duration.

Dependencies:

- Zustand.

Used By:

- Toast provider and pages.

Important Notes:

- ID counter is module-local.

#### `frontend/src/store/useChatbotStore.js`

Purpose:
Chatbot state management.

Responsibilities:

- Maintains chatbot open/close state.
- Stores message history.
- Provides actions to toggle chatbot, add messages, and clear messages.
- Initializes with a welcome bot message.

Dependencies:

- Zustand.

Used By:

- `ChatbotButton.jsx`, `ChatbotWindow.jsx`.

Important Notes:

- Non-persisted store (state resets on page refresh).
- Messages include id, type (user/bot), text, and timestamp.
- Bot responses are simulated on the frontend; can be extended to call backend endpoint.

#### `frontend/src/components/ProtectedRoute.jsx`

Purpose:
Route guard component.

Responsibilities:

- Redirects unauthenticated users to `/login`.
- Redirects role-mismatched users to `/unauthorized`.
- Renders nested routes via `Outlet`.

Dependencies:

- React Router.
- Auth store.

Used By:

- `App.jsx`.

Important Notes:

- Uses `useAuthStore.getState()` rather than subscribing through the hook.

#### `frontend/src/components/Layout.jsx`

Purpose:
Authenticated shell layout.

Responsibilities:

- Renders sidebar navigation based on role.
- Renders topbar with page title, notifications dropdown, mark-all-read action, and logout.
- Polls notifications every 30 seconds.
- Provides outlet area for pages.

Dependencies:

- Auth store, API client, React Router, Lucide icons.

Used By:

- Protected route tree.

Important Notes:

- Notifications endpoint is `/api/auth/notifications/`.

#### `frontend/src/components/ToastProvider.jsx`

Purpose:
Visual toast renderer.

Responsibilities:

- Subscribes to toast store.
- Renders stacked toast messages with dismiss buttons/icons.

Dependencies:

- Toast store.

Used By:

- `App.jsx`.

Important Notes:

- Mounted outside `BrowserRouter`.

#### `frontend/src/components/Spinner.jsx`

Purpose:
Reusable loading spinner.

Responsibilities:

- Renders a configurable size spinner icon.

Dependencies:

- CSS animation classes.

Used By:

- Pages and login.

Important Notes:

- Defaults to primary text color.

#### `frontend/src/components/ChatbotButton.jsx`

Purpose:
Floating action button for opening/closing the chatbot window.

Responsibilities:

- Renders a fixed position button in bottom-right corner.
- Toggles chatbot open/close state via Zustand store.
- Changes appearance based on open/close state (blue message circle when closed, red X when open).
- Uses Lucide React `MessageCircle` and `X` icons.

Dependencies:

- Zustand `useChatbotStore`.
- Lucide React icons.
- Tailwind CSS.

Used By:

- `Layout.jsx`.

Important Notes:

- Uses z-index 50 to stay above other UI elements.
- Scales and color-changes on state toggle for visual feedback.

#### `frontend/src/components/ChatbotWindow.jsx`

Purpose:
Chatbot conversation window component.

Responsibilities:

- Displays chat messages in a modal-like window.
- Handles user message input and submission.
- Auto-scrolls to latest message.
- Simulates bot responses with 500ms delay.
- Shows message timestamps.
- Only renders when chatbot is open.

Dependencies:

- Zustand `useChatbotStore`.
- Lucide React icons (`Send`, `X`).
- React hooks (`useState`, `useRef`, `useEffect`).

Used By:

- `Layout.jsx`.

Important Notes:

- Bot messages are simulated with random responses; no backend integration yet.
- Window animates in with `slideUp` animation (defined in `index.css`).
- Uses glass-morphism styling with gradients and shadows.
- Messages section is auto-scrollable.

## Frontend State Management

#### `frontend/src/pages/Login.jsx`

Purpose:
Login and public booking entry screen.

Responsibilities:

- Collects username/password.
- Calls auth store login.
- Navigates to `/` on success.
- Offers navigation to `/book`.

Dependencies:

- Auth store, toast store, router, spinner, icons.

Used By:

- `/login` route.

Important Notes:

- Placeholder says identifier, but backend expects `username`.

#### `frontend/src/pages/Dashboard.jsx`

Purpose:
Dashboard analytics page.

Responsibilities:

- Fetches `/dashboard/stats/`.
- Displays cards and Chart.js doughnut/bar charts.

Dependencies:

- API client, toast store, Chart.js, spinner.

Used By:

- `/` protected route.

Important Notes:

- Expects global aggregate stats from backend.

#### `frontend/src/pages/Patients.jsx`

Purpose:
Patient management page.

Responsibilities:

- Lists, searches, creates, edits, views, deletes patients.
- Uses modal forms and pagination.

Dependencies:

- API client, toast store, spinner, icons.

Used By:

- `/patients` protected route.

Important Notes:

- Calls `/patients/?search=...` after a debounce.

#### `frontend/src/pages/Appointments.jsx`

Purpose:
Appointment management page.

Responsibilities:

- Lists appointments with patient/doctor details.
- Fetches patients and doctors for scheduling.
- Creates, edits, deletes, confirms, and cancels appointments.
- Prevents client-side scheduling in the past.

Dependencies:

- API client, toast store, spinner, icons.

Used By:

- `/appointments` protected route.

Important Notes:

- Doctor options come from `/auth/users/` filtered client-side by role.

#### `frontend/src/pages/Consultations.jsx`

Purpose:
Consultation and AI assistance page.

Responsibilities:

- Manages symptom list.
- Calls AI analysis endpoint.
- Creates consultation records.
- Lists/searches/deletes past consultations.

Dependencies:

- API client, toast store, auth store, spinner, icons.

Used By:

- `/consultations` protected route for doctors/admins.

Important Notes:

- Code initializes secretary tab behavior, but route guard does not currently allow secretaries into this page.

#### `frontend/src/pages/Prescriptions.jsx`

Purpose:
Prescription management page.

Responsibilities:

- Lists prescriptions and consultations.
- Creates, edits, duplicates, deletes prescriptions.
- Downloads PDF exports.

Dependencies:

- API client, toast store, spinner, icons.

Used By:

- `/prescriptions` protected route for doctors/secretaries/admins.

Important Notes:

- PDF download uses blob response and browser object URL.

#### `frontend/src/pages/PublicBooking.jsx`

Purpose:
Unauthenticated public appointment booking wizard.

Responsibilities:

- Loads public doctor list.
- Loads available slots for selected doctor/date.
- Collects patient details.
- Posts booking request.
- Displays success state.

Dependencies:

- Axios direct calls, toast store, router, spinner, icons.

Used By:

- `/book` public route.

Important Notes:

- Hardcodes `API_URL = 'http://localhost:8000/api'` instead of using `VITE_API_BASE_URL`.

#### `frontend/src/pages/PatientPortal.jsx`

Purpose:
Espace patient for authenticated patients to track their appointments.

Responsibilities:
- Loads the authenticated patient's appointments.
- Displays upcoming and past appointments with status badges.
- Provides a clean logout option and links to the public booking page.

Dependencies:
- `useAuthStore`, `useThemeStore`, `api`, `useToastStore`, `lucide-react`.

Used By:
- `/my-appointments` patient route.

Important Notes:
- Renders using the global glass/mesh styling but excludes the clinic sidebar and topbar layout.

## Frontend Styles And Config

#### `frontend/src/index.css`

Purpose:
Primary app stylesheet.

Responsibilities:

- Imports Google fonts and Tailwind layers.
- Defines design tokens, layout, cards, buttons, tables, modals, animations, glass/mesh background styles.

Dependencies:

- Tailwind/PostCSS.

Used By:

- `main.jsx`.

Important Notes:

- Body overflow is hidden; app layout handles internal scrolling.

#### `frontend/src/App.css`

Purpose:
Leftover Vite/template stylesheet.

Responsibilities:

- Contains template-style classes such as counter/hero/docs.

Dependencies:

- Not imported by current `App.jsx`.

Used By:

- Likely unused.

Important Notes:

- Do not assume it affects the current app unless imported.

#### `frontend/tailwind.config.js`

Purpose:
Tailwind content configuration.

Responsibilities:

- Scans `index.html` and `src` files for classes.

Dependencies:

- Tailwind CSS.

Used By:

- PostCSS/Tailwind build.

Important Notes:

- Custom theme extension is currently minimal.

#### `frontend/postcss.config.js`

Purpose:
PostCSS setup.

Responsibilities:

- Enables Tailwind and Autoprefixer.

Dependencies:

- Tailwind CSS, Autoprefixer.

Used By:

- Vite CSS pipeline.

Important Notes:

- Standard Vite/Tailwind config.

#### `frontend/eslint.config.js`

Purpose:
Frontend lint configuration.

Responsibilities:

- Configures ESLint for React and browser globals.

Dependencies:

- ESLint packages from `package.json`.

Used By:

- `npm run lint`.

Important Notes:

- Check this before broad frontend edits.

#### `frontend/index.html`

Purpose:
Vite HTML shell.

Responsibilities:

- Provides root DOM node and loads frontend entry script.

Dependencies:

- `src/main.jsx`.

Used By:

- Vite dev/build.

Important Notes:

- Browser entry shell.

#### `frontend/package-lock.json`

Purpose:
Locked npm dependency graph.

Responsibilities:

- Pins exact frontend package versions.

Dependencies:

- `package.json`.

Used By:

- `npm install` / reproducible builds.

Important Notes:

- Update when dependencies change.

## Project Documentation & Report Tools

#### `generate_report.py`

Purpose:
Programmatic PDF compilation script for MedPredict's technical project report.

Responsibilities:
- Extracts school logos from the template and draws them in the page headers.
- Implements dynamic page numbering in the page footers.
- Generates cover page, acknowledgements, abstracts, table of contents, lists of figures and tables, and the chapters covering context, design, realization, and testing.

Dependencies:
- `reportlab`, PIL (pillow), Python standard libraries.

Used By:
- Developers compiling the project report document.

Important Notes:
- Execution: `python3 generate_report.py` or inside the backend container if reportlab isn't installed on the host.
