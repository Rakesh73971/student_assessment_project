# Student Assessment API

AI-powered REST API for student assessment, practice sessions, and score tracking built with FastAPI, PostgreSQL/Supabase, and Google Gemini AI.

## Features

- **Student Onboarding**: Register students, create profiles, join cohorts
- **Practice Sessions**: Students take practice tests with multiple question types
- **Score Tracking**: Automated scoring, performance analytics, and leaderboards
- **AI-Powered Assessment**: Google Gemini integration for intelligent question evaluation
- **Role-Based Access Control**: Student, Instructor, and Admin roles with Row Level Security
- **Cohort Management**: Organize students into cohorts for better management
- **Comprehensive Logging**: Request logging, error tracking, audit trails

## Tech Stack

- **Framework**: FastAPI (Python web framework)
- **Database**: PostgreSQL with Supabase (Row Level Security support)
- **ORM**: SQLAlchemy 2.0 (async-ready)
- **Database Bootstrap**: Supabase SQL script in `supabase/schema.sql`
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **AI Integration**: Google Gemini API
- **Testing**: pytest with pytest-asyncio
- **Deployment**: Railway/Render (Docker support)
- **CI/CD**: GitHub Actions
- **Technical Spec**: `TECH_SPEC.md`

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # Auth + DB dependencies (JWT, roles)
│   │   └── routers/
│   │       ├── auth_routes.py    # Authentication endpoints
│   │       ├── student_routes.py # Student profile endpoints
│   │       └── test_routes.py    # Test and practice endpoints
│   ├── core/
│   │   ├── config.py            # Settings from environment
│   │   └── security.py          # JWT and password utilities
│   ├── db/
│   │   ├── base.py              # SQLAlchemy Base
│   │   └── database.py          # Database connection and session
│   ├── models/
│   │   ├── user.py              # User model (authentication)
│   │   ├── student.py           # Student profile model
│   │   ├── cohort.py            # Cohort/class model
│   │   ├── test.py              # Test/assessment model
│   │   ├── question.py          # Question model
│   │   ├── practice_session.py   # Practice session tracking
│   │   ├── response.py          # Student response model
│   │   └── score.py             # Score tracking model
│   ├── schemas/
│   │   ├── auth.py              # Auth request/response schemas
│   │   ├── student.py           # Student schemas
│   │   ├── test.py              # Test and session schemas
│   │   └── response.py          # Response schemas
│   ├── services/
│   │   ├── auth_services.py      # Authentication business logic
│   │   ├── student_services.py   # Student profile logic
│   │   ├── test_services.py      # Test/session logic
│   │   └── ai_service.py         # Google Gemini API integration
│   └── main.py                   # FastAPI app initialization
├── tests/
│   ├── conftest.py              # pytest configuration
│   ├── test_auth.py             # Authentication tests
│   ├── test_student.py          # Student profile tests
│   └── test_tests.py            # Test/practice tests
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
└── README.md                    # This file
```

## Database Schema

### Users Table

- JWT-based authentication with bcrypt hashing
- Role-based access: STUDENT, INSTRUCTOR, ADMIN
- Profile fields: email, username, full_name, bio

### Students Table

- Linked to Users (one-to-one)
- Cohort assignment
- Profile information: grade_level, school_name
- Relationships: practice_sessions, responses, scores

### Cohorts Table

- Group students for instructor management
- Linked to instructor
- Contains multiple tests and students

### Tests Table

- Assessment types: PRACTICE, ASSESSMENT, QUIZ
- Question management
- Passing score threshold
- Publication status

### Questions Table

- Multiple question types: multiple_choice, short_answer, essay, true_false
- Correct answers and explanations
- Point values

### Practice Sessions Table

- Track student test attempts
- Start/completion times
- Score calculation
- AI-generated feedback

### Responses Table

- Individual student answers
- Automatic and AI-assisted grading
- Points earned tracking

### Scores Table

- Aggregate performance tracking
- Attempt numbering
- Pass/fail status

## Environment Setup

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ or Supabase account
- Google API key

### Installation

1. **Clone the repository**

   ```bash
   cd backend
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**

   ```bash
   # Supabase/PostgreSQL:
   # Run supabase/schema.sql in the Supabase SQL editor or with psql.

   # Local development can also auto-create SQLAlchemy tables on startup.
   ```

6. **Run the server**

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

7. **Access API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token
- `GET /api/v1/auth/me` - Get current user profile
- `PUT /api/v1/auth/me/profile` - Update user profile

### Students

- `GET /api/v1/students/me` - Get my profile
- `PUT /api/v1/students/me` - Update my profile
- `GET /api/v1/students/{student_id}` - Get student profile
- `GET /api/v1/students/cohort/{cohort_id}` - List cohort students

### Tests & Practice

- `POST /api/v1/tests/` - Create test (instructor)
- `GET /api/v1/tests/{test_id}` - Get test details
- `PUT /api/v1/tests/{test_id}` - Update test (instructor)
- `POST /api/v1/tests/{test_id}/questions` - Add question (instructor)
- `POST /api/v1/tests/sessions/start` - Start practice session
- `POST /api/v1/tests/sessions/{session_id}/submit-response` - Submit answer
- `POST /api/v1/tests/sessions/{session_id}/complete` - Complete session
- `GET /api/v1/tests/scores/my` - Get my scores

## Authentication

The API uses JWT-based authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "securepassword123"
  }'
```

## Data Models

### User Roles

- **STUDENT**: Takes tests, submits responses, views scores
- **INSTRUCTOR**: Creates tests, manages cohorts, views student scores
- **ADMIN**: Full access, user management

### Question Types

- **MULTIPLE_CHOICE**: Standard multiple choice questions
- **SHORT_ANSWER**: Text-based short answers (AI-evaluated)
- **ESSAY**: Long-form essays (AI-evaluated)
- **TRUE_FALSE**: Binary true/false questions

### Test Types

- **PRACTICE**: Non-graded practice attempts
- **ASSESSMENT**: Formal assessments (graded)
- **QUIZ**: Quick quizzes (graded)

## AI Integration

The API uses Google Gemini for intelligent assessment:

1. **Response Evaluation**: Evaluates open-ended answers
   - Assesses conceptual understanding
   - Provides fair partial credit
   - Generates explanations

2. **Feedback Generation**: Creates personalized feedback
   - Highlights strengths
   - Identifies areas for improvement
   - Provides study recommendations

3. **Learning Gap Analysis**: Analyzes performance patterns
   - Identifies weak areas
   - Suggests review topics
   - Recommends study strategies

## Testing

Run the test suite:

```bash
# All tests
pytest

# Specific test file
pytest tests/test_auth.py

# With coverage
pytest --cov=app tests/
```

## Deployment

### Docker

```bash
docker build -t student-assessment-api .
docker run -p 8000:8000 --env-file .env student-assessment-api
```

### Railway

```bash
railway up
```

### Render

1. Connect your GitHub repository
2. Set environment variables in Render dashboard
3. Deploy directly from Git

## CI/CD with GitHub Actions

The repository includes GitHub Actions workflow for:

- Running tests on push
- Building Docker image
- Deploying to Railway/Render
- Code quality checks

See `.github/workflows/` for configuration.

## Security Considerations

- ✅ JWT tokens with expiration
- ✅ Password hashing with bcrypt
- ✅ Role-based access control
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS configuration
- ✅ Trusted host middleware
- ⚠️ TODO: Rate limiting
- Supabase schema and baseline Row Level Security policies in `supabase/schema.sql`

## Logging

All endpoints and errors are logged with:

- Request/response details
- User identification
- Timestamps
- Error stack traces

Access logs in the terminal or configure file rotation.

## Performance Considerations

- Database connection pooling
- Query optimization with proper indexes
- Async request handling
- Response pagination (limit 500 items)
- AI API call caching (recommended)

## Known Limitations & TODOs

- [ ] Add rate limiting middleware
- [ ] Implement email verification
- [ ] Add password reset flow
- [ ] Implement file uploads for attachments
- [ ] Add bulk import for students/tests
- [ ] Implement caching strategy
- [ ] Add WebSocket support for real-time updates

## Troubleshooting

### Database Connection Error

```
Check .env file database variables
Ensure PostgreSQL/Supabase is running
Verify network connectivity
```

### API key 401 errors

```
Verify Google API key is set
Check token hasn't expired
Ensure Bearer token is formatted correctly
```

### Test data not persisting

```
Check database connection
For Supabase/PostgreSQL, verify supabase/schema.sql has been applied
Verify user has appropriate role
```

## Contributing

1. Create feature branch (`git checkout -b feature/AmazingFeature`)
2. Commit changes (`git commit -m 'Add AmazingFeature'`)
3. Push to branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:

- GitHub Issues: [Create an issue](https://github.com/yourrepo/issues)
- Email: support@example.com

## Changelog

### v1.0.0 (2024)

- Initial release
- Core functionality for student assessment
- AI-powered evaluation
- Role-based access control
