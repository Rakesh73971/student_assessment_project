# Student Assessment Platform

Full-stack student assessment app with a FastAPI backend, React frontend, Supabase/PostgreSQL database, cohort-based test assignment, score tracking, and Google Gemini-powered semantic answer evaluation.

## Features

- Student and instructor registration/login with JWT authentication.
- Role-based access for students, instructors, and admins.
- Student onboarding with profile and cohort support.
- Instructor dashboard for creating cohorts, tests, and questions.
- Practice session flow for students to start tests, submit answers, complete sessions, and view scores.
- AI answer evaluation based on meaning, not exact word matching.
- Supabase/PostgreSQL schema with indexes, relationships, RLS policies, and migrations.
- Backend tests, frontend lint/build, Docker support, and GitHub Actions CI.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, PostgreSQL, Pydantic, JWT auth.
- Frontend: React, Vite, Axios, React Router, Lucide icons.
- Database: Supabase PostgreSQL.
- AI: Google Gemini through `google-genai`.
- CI/CD: GitHub Actions.
- Deployment support: Docker, Railway/Render-ready backend.

## Project Structure

```text
Student Assessment/
  backend/
    app/
      api/routers/        FastAPI route modules
      core/               config and security
      db/                 database session and RLS context
      models/             SQLAlchemy models
      schemas/            Pydantic schemas
      services/           auth, student, test, AI logic
    supabase/
      schema.sql          full Supabase bootstrap schema
      migrations/         SQL migrations for existing DBs
    tests/                backend test suite
    Dockerfile
    docker-compose.yml
    requirements.txt
  frontend/
    src/
      api/                API client
      contexts/           auth context
      pages/              login, dashboards, tests, results
      components/         shared layout
    package.json
  .github/workflows/
    ci.yml                backend, frontend, Docker checks
```

## Environment Setup

Create `backend/.env`:

```env
DATABASE_HOSTNAME=db.your-project-ref.supabase.co
DATABASE_PORT=5432
DATABASE_PASSWORD=your_supabase_database_password
DATABASE_NAME=student_assessment
DATABASE_USERNAME=postgres

SECRET_KEY=change_this_to_a_long_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

GOOGLE_API_KEY=your_google_api_key_here

DEBUG_MODE=True
ENVIRONMENT=development
APP_NAME=Student Assessment API
APP_VERSION=1.0.0
REQUEST_SLOW_MS=800
ENABLE_DB_RLS_CONTEXT=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

Do not commit `.env`. Use `.env.example` only for placeholders.

## Supabase Setup

1. Create a Supabase project.
2. Open **SQL Editor**.
3. Run `backend/supabase/schema.sql`.
4. Confirm tables exist: `users`, `students`, `cohorts`, `tests`, `questions`, `practice_sessions`, `responses`, `scores`.
5. Add the Supabase database host, database name, username, password, and port to `backend/.env`.

For an existing Supabase database, run migrations in order from:

```text
backend/supabase/migrations/
```

## Run Backend

```powershell
cd "C:\Users\Rakes\OneDrive\Desktop\FastAPI full stack\Student Assessment\backend"
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend docs:

```text
http://127.0.0.1:8000/docs
```

## Run Frontend

```powershell
cd "C:\Users\Rakes\OneDrive\Desktop\FastAPI full stack\Student Assessment\frontend"
npm install
npm run dev
```

Frontend dev server usually runs at:

```text
http://localhost:5173
```

## Testing

The backend test suite must not run against the real Supabase production database because tests create and drop tables. Use GitHub Actions or a separate local/Postgres test database.

Safe checks that do not need a live test DB:

```powershell
cd "C:\Users\Rakes\OneDrive\Desktop\FastAPI full stack\Student Assessment\backend"
pytest tests/test_ai_service.py tests/test_deployment_files.py tests/test_supabase_schema.py
```

Full backend tests with a separate test DB:

```powershell
$env:TEST_DATABASE_NAME="student_assessment_test"
pytest -v
```

Frontend checks:

```powershell
cd "C:\Users\Rakes\OneDrive\Desktop\FastAPI full stack\Student Assessment\frontend"
npm run lint
npm run build
```

## Docker

Docker is optional. It is useful for backend deployment or local container testing.

```powershell
cd "C:\Users\Rakes\OneDrive\Desktop\FastAPI full stack\Student Assessment\backend"
docker build -t student-assessment-api .
docker run -p 8000:8000 --env-file .env student-assessment-api
```

With compose:

```powershell
docker compose up --build
```

If your Docker installation uses the old command:

```powershell
docker-compose up --build
```

## CI/CD

GitHub Actions workflow:

```text
.github/workflows/ci.yml
```

It checks:

- Backend tests against a temporary Postgres service.
- Frontend lint.
- Frontend production build.
- Backend Docker image build.

## Deployment Notes

Backend can be deployed to Railway or Render using the backend Dockerfile or Python start command:

```text
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set all backend environment variables in the deployment dashboard. Do not upload local `.env` files.

Frontend can be deployed as a Vite static site after:

```powershell
npm run build
```

## Important Safety Notes

- Rotate any API key or database password that was pasted into chat or committed by mistake.
- Never run destructive tests against your real Supabase database.
- Keep `GOOGLE_API_KEY`, `DATABASE_PASSWORD`, and `SECRET_KEY` only in environment variables.
- If using Supabase RLS, keep `ENABLE_DB_RLS_CONTEXT=True` so the API sets database user context during authenticated requests.
