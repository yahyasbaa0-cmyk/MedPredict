# MedPredict Agent Memory

Read this before starting future tasks.

## Required Pre-Task Reading

Before changing code, read:

- `docs/knowledge/PROJECT_OVERVIEW.md`
- `docs/knowledge/FILE_INDEX.md`
- `docs/knowledge/ARCHITECTURE.md`
- `docs/knowledge/AGENT_MEMORY.md`
- `docs/knowledge/MISTAKES.md`

Then update the knowledge docs after any code change.

## Architecture

MedPredict is a three-service app plus database: React/Vite frontend, Django REST backend, Flask AI service, and Postgres via Docker Compose.

The backend can run with SQLite when `POSTGRES_HOST` is absent. Docker Compose sets Postgres environment variables and uses Postgres.

## Local Startup

Use `make setup` for full local bootstrap. It runs Docker Compose build/up, waits for Postgres, applies migrations, creates the default admin if missing, seeds demo data, trains the AI model, and prints service URLs.

Important Makefile targets:

- `make up`: start services.
- `make migrate`: apply migrations.
- `make seed`: run `backend/seed_data.py`.
- `make train-ai`: run `ai_service/model/train.py`.
- `make logs`: follow logs.
- `make down`: stop services.
- `make clean`: stop services and remove volumes.

`make seed` is destructive for demo/domain records because `backend/seed_data.py` deletes prescriptions, consultations, appointments, patients, and non-superuser users before recreating demo data.

## Authentication

The backend uses SimpleJWT. `accounts.serializers.CustomTokenObtainPairSerializer` adds role/email/name claims. The frontend decodes the access token manually in `useAuthStore.js` and does not fetch a separate current-user endpoint.

`ProtectedRoute` redirects role mismatches to `/unauthorized`, but no explicit unauthorized route exists. The catch-all route will navigate back to `/`.

## Roles And Scoping

Roles are `ADMIN`, `DOCTOR`, `SECRETARY`, and `PATIENT`.

Doctors are scoped in backend querysets:

- Patients: appointments with doctor OR created by doctor.
- Appointments: doctor field equals current user.
- Consultations: appointment doctor equals current user.
- Prescriptions: consultation appointment doctor equals current user.

Secretary permissions (updated 2026-06-20):

- Patients: full CRUD (create, read, update) via `IsAdminOrDoctorOrSecretary`. Delete is hidden in frontend but not blocked by backend; only hidden in UI.
- Appointments: full CRUD via `IsAdminOrDoctorOrSecretary`. Secretaries can create, edit, confirm, cancel, and delete appointments.
- Consultations: fully blocked via `IsDoctorOrAdmin`. Frontend route guard also excludes secretaries.
- Prescriptions: read-only + PDF download via `IsSecretaryReadOnly`. Frontend hides create/edit/delete buttons.

Permission classes in `accounts/permissions.py`:

- `IsAdminOrDoctorOrSecretary`: full CRUD for all authenticated staff. Used on patients and appointments.
- `IsDoctorOrAdmin`: blocks SECRETARY from all operations. Used on consultations.
- `IsSecretaryReadOnly`: read-only for SECRETARY, full CRUD for others. Used on prescriptions.

Dashboard stats are not role-scoped; any authenticated user gets global aggregates.

## Appointment Rules

`Appointment.save()` calls `clean()`.

Validation prevents:

- Same doctor, same date, same exact time, unless cancelled.
- More than 8 non-cancelled appointments for one doctor on one day.

Validation does not check duration overlap, only exact time equality.

Public available slots are hardcoded:

- `09:00`
- `09:30`
- `10:00`
- `11:00`
- `14:00`
- `15:30`
- `16:00`
- `17:00`

## Public Booking

Public booking endpoints are unauthenticated. Public booking finds or creates patients by CIN and defaults date of birth to `2000-01-01` if missing.

Frontend `PublicBooking.jsx` hardcodes `http://localhost:8000/api` instead of using the shared Axios client or `VITE_API_BASE_URL`.

## Patient Portal & Auto-Account Creation

Implemented on 2026-06-20 to allow patients to track their booked appointments.

- **Auto-Account Creation**: When a patient books an appointment via the public `/book` page, the backend automatically checks if the patient already has an associated user account. If not, it creates a `User` account with role `PATIENT`, `username` = CIN, and `password` = CIN + "2025" (e.g., `AB1234562025`).
- **Success Screen Credentials**: The credentials (`username` and `password`) are returned in the API booking response and displayed in a dedicated credentials block on the booking confirmation screen. Returning patients see a prompt to log in with their existing credentials.
- **Login Redirect & Routing**: Authenticated patients logging in are redirected to `/my-appointments` (Patient Portal). The main clinic routes are wrapped in a ProtectedRoute restricting access only to staff roles (`ADMIN`, `DOCTOR`, `SECRETARY`), while `/my-appointments` restricts access to the `PATIENT` role. Mismatches automatically redirect patients to `/my-appointments` and staff to `/`.
- **My Appointments API**: Protected GET `/api/appointments/my/` endpoint returns only the appointments of the authenticated patient.

## WhatsApp

WhatsApp booking state is stored in `WhatsAppSession` with the phone number as primary key.

The WhatsApp flow hardcodes doctor choices:

- `1` -> username `dr_bennani`
- `2` -> username `dr_chaoui`

Seed data creates those doctors. If they do not exist, WhatsApp appointment creation fails.

## AI Service & Groq Integration

The system previously used a local Flask-based `ai_service` container. On 2026-06-20, this was replaced with direct Groq API integration using Chat Completions:

- **Groq API**: Queries `https://api.groq.com/openai/v1/chat/completions` directly.
- **Environment**: Reads `GROQ_API_TOKEN` environment variable, configured via `.env` file mapped to the backend container in `docker-compose.yml`.
- **Model**: Uses model `"openai/gpt-oss-120b"` with a temperature of `0.2` and `"response_format": {"type": "json_object"}`.
- **Fail-safe**: Returns a 503 HTTP status code with empty predictions if the API request fails, or 502 Bad Gateway if the response structure is invalid.

## PDF Export

Prescription PDF generation lives entirely in `backend/prescriptions/views.py` using ReportLab. It uses patient city for "Fait a" and picks the request user as doctor only if the requester role is `DOCTOR`; otherwise it uses the consultation appointment doctor.

## Dark Mode

A complete dark mode system was implemented on 2026-06-19 using CSS variables and Zustand state management.

**Key Files:**
- `frontend/src/index.css`: Dark mode CSS variables in `[data-theme="dark"]` selector
- `frontend/src/store/useThemeStore.js`: Theme state management with localStorage persistence
- `frontend/src/components/ThemeToggle.jsx`: Moon/Sun toggle button in topbar
- `frontend/src/App.jsx`: Theme initialization on app load

**Theme Toggle:**
- Located in topbar next to logout button
- Moon icon = light mode active, click to switch to dark
- Sun icon = dark mode active, click to switch to light
- Persists to `localStorage.medpredict-theme`

**CSS Variables:**
- All components use `var(--variable-name)` for colors
- Light mode: bright backgrounds, dark text
- Dark mode: dark backgrounds, light text
- Semantic colors (primary, secondary, danger, success, warning) auto-adjust

**Component Updates:**
- ChatbotWindow/Button: Use CSS variables instead of hardcoded colors
- Dashboard: Chart colors adapt based on theme
- Login: Background uses `var(--bg-main)` instead of `#0f172a`
- Layout: All inline styles use CSS variables
- All modals, cards, inputs: Theme-aware

**Performance:**
- Zero JavaScript overhead - pure CSS switching
- No re-renders when theme changes
- Single DOM attribute: `document.documentElement.setAttribute('data-theme', theme)`
- Theme loads before first render (no flash)

**To Add Dark Mode to New Components:**
```css
/* In index.css */
--new-color: #light-value;

[data-theme="dark"] {
  --new-color: #dark-value;
}
```

```jsx
// In component
<div style={{ color: 'var(--new-color)' }}>Theme-aware text</div>
```

## Chatbot Feature

Frontend floating chatbot button and window are implemented as of 2026-06-19, and backend integration was completed on 2026-06-20:

- **ChatbotButton.jsx**: Fixed position floating button (bottom-right, z-index 50) that toggles the window.
- **ChatbotWindow.jsx**: Chat window displaying conversation history, message timestamps, dynamic input field, and a premium bouncing dots typing indicator when the AI assistant is thinking.
- **useChatbotStore.js**: Zustand store managing `isOpen` state, message array, adding new messages, and clearing message history.

**Groq API Backend Integration:**
- Exposes POST `/api/auth/chatbot/` endpoint.
- Maps conversation messages to a payload containing the current message and the previous 5 history messages for context.
- Calls Groq completions endpoint using the `openai/gpt-oss-120b` model.
- Instructs the model via system prompt to assume the **MedPredict Assistant** persona, a friendly clinic helper.
- Customizes responses contextually based on the authenticated user's name and role (`ADMIN`, `DOCTOR`, `SECRETARY`, `PATIENT`).
- Displays a clean error bubble on the chat UI in the event of an API or gateway timeout rather than failing or crashing.

**Styling Details:**
- Uses blue gradient header (primary to secondary colors).
- Messages are left-aligned for bot, right-aligned for user.
- Glass-morphism effect with backdrop blur on the window.
- `slideUp` animation defined in `index.css` for window entrance.
- Button changes from blue message circle to red X when open.

## Configuration Pitfalls

`init_db.sql` is UTF-16 little-endian with destructive DROP statements and was disabled on 2026-06-19. Do not re-enable it without converting to UTF-8 and validating all referenced tables exist.

`backend/requirements.txt` had encoding/null-byte corruption around the `twilio==9.10.9` line and was fixed on 2026-06-19 by rewriting it as plain ASCII text. If this build error returns, inspect the file bytes with `xxd`.

`frontend/vite.config.js` configures port 9654, but Docker Compose overrides the dev command to host on port 5173.

`CELERY_BROKER_URL` exists in Django settings, but no Redis service, Celery app, tasks, or worker are currently implemented.

## Styling

The active frontend styling is primarily `frontend/src/index.css` plus Tailwind classes. `frontend/src/App.css` appears to be leftover template CSS and is not imported by current `App.jsx`.

The UI uses a glass/mesh visual style and Lucide icons.

## Testing

Only `backend/consultations/tests.py` contains meaningful tests. It mocks AI calls for success and failure behavior.

Most app `tests.py` files are placeholders.

## Documentation Discipline

After every change:

- Update `CHANGE_LOG.md`.
- Update `FILE_INDEX.md` if important files changed or new important files were added.
- Update `AGENT_MEMORY.md` with new discoveries.
- Update `MISTAKES.md` if any mistake happened.
