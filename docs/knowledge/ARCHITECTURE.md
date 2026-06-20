# MedPredict Architecture

## Module Map

```mermaid
flowchart TB
    subgraph Frontend
        App[App.jsx routes]
        Layout[Layout + notifications]
        AuthStore[useAuthStore]
        API[Axios client]
        Pages[Dashboard/Patients/Appointments/Consultations/Prescriptions/PublicBooking]
    end

    subgraph Backend
        URLs[medpredict_api.urls]
        Accounts[accounts]
        Patients[patients]
        Appointments[appointments]
        Consultations[consultations]
        Prescriptions[prescriptions]
        Dashboard[dashboard]
    end

    subgraph AI
        Flask[Flask app.py]
        Train[model/train.py]
        Artifacts[model.pkl + features.joblib]
    end

    App --> Layout
    Pages --> API
    AuthStore --> API
    API --> URLs
    URLs --> Accounts
    URLs --> Patients
    URLs --> Appointments
    URLs --> Consultations
    URLs --> Prescriptions
    URLs --> Dashboard
    Consultations --> Flask
    Train --> Artifacts
    Flask --> Artifacts
```

## Backend Services

### Accounts

Responsibilities:

- Defines custom `User` model with `role` and `phone`.
- Defines `Notification`.
- Provides user and notification CRUD viewsets.
- Adds role/email/name custom claims to JWT tokens.
- Restricts user create/delete to authenticated admins.

### Patients

Responsibilities:

- Defines patient demographic and medical record fields.
- Validates Moroccan phone formats.
- Tracks creator via `created_by`.
- Exposes filtered/searchable patient CRUD.
- Scopes doctor access to patients with appointments for the doctor or patients created by that doctor.

### Appointments

Responsibilities:

- Defines appointment status lifecycle.
- Validates exact time-slot conflicts and daily capacity.
- Exposes authenticated appointment CRUD with doctor scoping.
- Creates doctor notifications when others schedule appointments.
- Exposes public doctors, available slots, and booking endpoints.
- Handles Twilio WhatsApp state machine.

### Consultations

Responsibilities:

- Links each consultation one-to-one with an appointment.
- Stores symptoms, examination, diagnosis, notes, and AI suggestions.
- Exposes CRUD with doctor scoping.
- Prevents secretaries from mutating consultations.
- Proxies symptom analysis to the AI service.

### Prescriptions

Responsibilities:

- Links prescriptions to consultations.
- Stores medication, dosage, posology, duration, and recommendations.
- Exposes CRUD with doctor scoping.
- Generates prescription PDF exports using ReportLab.

### Dashboard

Responsibilities:

- Aggregates total patients, doctors, recent consultations, pathology distribution, appointment status counts, and AI usage rate.

## Data Flow

### Authenticated API Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Django API
    participant DB as Database

    U->>F: Login credentials
    F->>B: POST /api/auth/login/
    B->>DB: Validate user
    B-->>F: JWT access/refresh with role claims
    F->>F: Store token in localStorage/Zustand
    F->>B: API request with Bearer token
    B->>DB: Query scoped data
    B-->>F: JSON response
```

### Appointment Booking Flow

```mermaid
flowchart LR
    Staff[Staff or public user] --> API[Appointment endpoint]
    API --> Patient[Find/create Patient]
    API --> Doctor[Resolve Doctor]
    API --> Validate[Appointment.clean]
    Validate -->|no conflict and under 8/day| Save[Save Appointment]
    Save --> Notify[Create Notification]
    Validate -->|conflict/full| Error[400 validation error]
```

### AI Flow

```mermaid
sequenceDiagram
    participant F as Frontend Consultations
    participant B as Django ConsultationViewSet
    participant A as Flask AI service
    participant M as joblib artifacts

    F->>B: POST /api/consultations/analyze-symptoms/
    B->>A: POST AI_SERVICE_URL with symptoms
    A->>M: Load/use model and feature names
    A-->>B: predictions + disclaimer
    B-->>F: predictions
```

Fail-safe behavior: if the Flask request raises a `requests` exception or returns a bad status, Django returns 503 with `{predictions: [], error: "AI Service unavailable"}`.

## Database Flow

Primary domain relationships:

```mermaid
erDiagram
    User ||--o{ Notification : receives
    User ||--o{ Patient : creates
    User ||--o{ Appointment : doctor
    Patient ||--o{ Appointment : has
    Appointment ||--|| Consultation : produces
    Consultation ||--o{ Prescription : has
    WhatsAppSession {
        string phone_number PK
        string state
        json data
        datetime updated_at
    }
```

Key tables/models:

- `accounts.User`: Django auth user plus `role` and `phone`.
- `accounts.Notification`: per-user notification feed.
- `patients.Patient`: patient identity, contact details, medical metadata, archive flag, creator.
- `appointments.Appointment`: patient, doctor, date, time, duration, reason, status.
- `appointments.WhatsAppSession`: Twilio conversation state.
- `consultations.Consultation`: appointment-linked clinical record and AI suggestions.
- `prescriptions.Prescription`: consultation-linked medication plan.

## API Flow

Root Django routes:

- `/api/auth/`
- `/api/patients/`
- `/api/appointments/`
- `/api/consultations/`
- `/api/prescriptions/`
- `/api/dashboard/`
- `/swagger/`
- `/redoc/`

Important custom endpoints:

- `POST /api/auth/login/`
- `POST /api/auth/token/refresh/`
- `PATCH /api/auth/notifications/mark_all_read/`
- `POST /api/appointments/public/book/`
- `GET /api/appointments/public/doctors/`
- `GET /api/appointments/public/available-slots/`
- `POST /api/appointments/whatsapp/webhook/`
- `POST /api/consultations/analyze-symptoms/`
- `GET /api/prescriptions/{id}/export-pdf/`
- `GET /api/dashboard/stats/`

## Frontend Flow

```mermaid
flowchart TD
    main[main.jsx] --> App[App.jsx]
    App --> Toast[ToastProvider]
    App --> Login[/login]
    App --> Book[/book public]
    App --> Guard[ProtectedRoute]
    Guard --> Layout[Layout with Sidebar/Topbar]
    Layout --> Dashboard[/]
    Layout --> Patients[/patients]
    Layout --> Appointments[/appointments]
    Layout --> Consultations[/consultations doctor/admin]
    Layout --> Prescriptions[/prescriptions doctor/secretary/admin]
```

The authenticated Axios client:

- Uses `VITE_API_BASE_URL` or `http://localhost:8000/api`.
- Adds `Authorization` header from `localStorage.medpredict_token`.
- Clears token/user keys and redirects to `/login` on HTTP 401.

## Worker Flow

There is no active worker process in the current repository.

Notable related settings:

- `CELERY_BROKER_URL = 'redis://redis:6379/0'` exists.
- No `celery.py`, tasks modules, Redis service, or worker command are present.

Treat Celery as a future/unused configuration unless new code introduces it.
