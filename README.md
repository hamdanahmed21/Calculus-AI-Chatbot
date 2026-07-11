# 🧮 CalcVoyager — AI-Powered Multivariable Calculus Tutor

A full-stack adaptive learning platform for multivariable calculus with real-time AI tutoring, session persistence, feedback collection, and intelligent difficulty scaling.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [API Endpoints](#api-endpoints)
8. [Testing](#testing)
9. [Development](#development)

---

## 🎯 Overview

CalcVoyager is a three-tier web application designed to provide personalized calculus tutoring through an AI chatbot (Cal). Students interact with Cal through a React frontend, which communicates with a Starlette backend, which in turn calls a FastAPI AI service powered by xAI's Grok LLM.

### Key Objectives (CBs)

- **CB-2**: System prompt validation and calculus tutoring quality
- **CB-8**: Scope enforcement (refuse off-topic questions)
- **CB-9**: Response quality evaluation with answer keys
- **CB-11/CB-14**: Rate limiting (50/day for authenticated, 10/session for guests)
- **CB-12**: Message feedback (like/dislike) and integration with adaptive difficulty
- **CB-13**: Session summarization for context window management
- **CB-16**: Symbolic math verification using SymPy
- **CB-18**: Adaptive difficulty tracking per topic
- **CB-19**: Study sheet export (Markdown)
- **CB-20**: Circuit breaker and response caching for LLM resilience
- **CB-22**: GitHub Actions test automation

---

## 🏗️ Architecture

```
Frontend (React)
    ↓
Backend (Starlette) ← SQLite Database
    ↓
AI Service (FastAPI)
    ↓
xAI Grok LLM
```

### Stack

- **Frontend**: React.js with KaTeX math rendering
- **Backend**: Starlette (Python async web framework)
- **AI Service**: FastAPI with OpenAI SDK (xAI Grok)
- **Database**: SQLite (aiosqlite for async access)
- **Verification**: SymPy for symbolic math validation
- **CI/CD**: GitHub Actions with mock and real API testing

---

## ✨ Features

### 1. **Real-Time Streaming Chat** (CB-10)
- SSE-based streaming for token-by-token LLM output
- Fallback to non-streaming if streaming unavailable
- Progress indicators and typing animations

### 2. **Session Persistence** (CB-13)
- Authenticated users have persistent chat sessions
- Automatic session summarization every 10 messages
- Session export as downloadable Markdown study sheets (CB-19)

### 3. **Message Feedback** (CB-12)
- Like/dislike buttons on every assistant response
- Authenticated users' feedback persisted to database
- Guests can rate locally (not persisted)
- Feedback feeds into adaptive difficulty calculations

### 4. **Adaptive Difficulty** (CB-18)
- Per-topic difficulty tracking (beginner/intermediate/advanced)
- Score-based level calculation with thresholds
- Like/dislike and message count drive difficulty adjustments
- Frontend displays difficulty badge

### 5. **Rate Limiting** (CB-11/CB-14)
- **Authenticated users**: 50 messages/day (keyed by user_id)
- **Guests**: 10 messages/session (keyed by IP/session)
- HTTP 429 responses with `retry_after` header
- Friendly inline error messages on frontend

### 6. **Symbolic Math Verification** (CB-16)
- Automatic verification of mathematical answers using SymPy
- Supports single and multivariable expressions
- Partial derivatives w.r.t. named variables (x, y, z, etc.)
- Graceful fallback for unsupported operations (vector calc, Lagrange)
- Returns None for unparseable problems (no crash)

### 7. **Scope Enforcement** (CB-8)
- Cal refuses off-topic questions
- Validates all responses against calculus keywords
- Logs scope violations for monitoring

### 8. **Response Quality** (CB-9)
- Answer key matching for correctness evaluation
- LaTeX formatting validation
- Word count limits per response type
- Follow-up suggestions included in every response

### 9. **Circuit Breaker & Caching** (CB-20)
- Opens after 3 consecutive LLM failures
- Resets after 60 seconds (half-open trial)
- 5-minute response cache by message+topic+difficulty
- Graceful fallback to mock responses on failures

---

## 🚀 Installation

### Prerequisites

- Python 3.11+ (or 3.12 for CI)
- Node.js 18+ (for frontend)
- pip and npm package managers
- xAI Grok API key (for real testing)

### Backend Setup

```bash
# Install Python dependencies
pip install -r aiService/requirements.txt
pip install -r backend/requirements.txt

# Create .env files
mkdir -p aiService/services
cat > aiService/services/.env << EOF
GROK_API_KEY=xai_your_actual_key_here
USE_MOCK=False
CIRCUIT_FAILURE_THRESHOLD=3
CIRCUIT_RESET_SECONDS=60
PRIMARY_TIMEOUT_SECONDS=12
LLM_CACHE_TTL_SECONDS=300
EOF

# Create database
cd backend
python -c "from app.database.db import init_db; import asyncio; asyncio.run(init_db())"
```

### Frontend Setup

```bash
cd frontend
npm install
```

---

## ⚙️ Configuration

### Environment Variables

#### AI Service (`aiService/services/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `GROK_API_KEY` | (required) | xAI API key for Grok LLM |
| `USE_MOCK` | `True` | Use mock LLM instead of real API (for testing) |
| `CIRCUIT_FAILURE_THRESHOLD` | `3` | Failures before circuit opens |
| `CIRCUIT_RESET_SECONDS` | `60` | Time before half-open trial |
| `PRIMARY_TIMEOUT_SECONDS` | `12` | Request timeout for LLM |
| `LLM_CACHE_TTL_SECONDS` | `300` | Response cache TTL in seconds |

#### Frontend (`.env` or `frontend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://127.0.0.1:8002` | Backend Starlette URL |
| `REACT_APP_CHAT_URL` | `` | Standalone AI service URL (optional) |

---

## 🏃 Running the Application

### 1. Start the AI Service (Port 8001)

```bash
cd aiService
python -m uvicorn chatbot:app --host 127.0.0.1 --port 8001 --reload
```

### 2. Start the Backend (Port 8002)

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

### 3. Start the Frontend (Port 3000)

```bash
cd frontend
npm start
```

The application will be available at `http://localhost:3000`.

---

## 🔌 API Endpoints

### Chat Endpoints

#### `POST /api/chat`
Main chat endpoint. Accepts a message, returns response with metadata.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "What is a limit?"},
    {"role": "assistant", "content": "..."}
  ],
  "context": "Limits and Continuity",
  "topic_key": "limits",
  "page_url": "/calculus/limits"
}
```

**Response:**
```json
{
  "reply": "A limit describes...",
  "suggestions": ["What about...", "Can you explain..."],
  "message_id": 42,
  "session_id": "uuid-string",
  "difficulty": "intermediate"
}
```

#### `POST /api/chat/feedback`
Submit feedback (like/dislike) on a message (CB-12).

**Request:**
```json
{
  "message_id": 42,
  "session_id": "uuid-string",
  "feedback": "like"
}
```

#### `GET /api/chat/progress/{topic}`
Fetch adaptive difficulty level for a topic (CB-18).

**Response:**
```json
{
  "data": {
    "topic": "limits",
    "difficulty_level": "intermediate",
    "difficulty_score": 5.5,
    "message_count": 12,
    "like_count": 3,
    "dislike_count": 1
  }
}
```

#### `GET /api/chat/sessions/{session_id}/export`
Download session as Markdown study sheet (CB-19).

**Response:** Markdown file with formulas digest + full Q&A trail.

### Session Endpoints

#### `POST /api/chat/sessions`
Create a new chat session.

#### `GET /api/chat/sessions`
List all sessions for the authenticated user.

#### `PUT /api/chat/sessions/{session_id}`
Update session title.

#### `DELETE /api/chat/sessions/{session_id}`
Soft-delete a session.

#### `GET /api/chat/history/{session_id}`
Fetch all messages in a session.

---

## 🧪 Testing

### Mock Mode Testing (CI/PRs)

```bash
# Set USE_MOCK=True in .env
cd aiService
python -m tests.chatbot_tests          # CB-2, CB-8, CB-9 validation
pytest tests/test_cb12_feedback.py     # CB-12 feedback unit tests
python tests/test_streaming_latency.py # Streaming performance
```

### Real API Testing (Nightly)

```bash
# Set USE_MOCK=False and provide GROK_API_KEY
cd aiService
python -m tests.chatbot_tests
```

### Test Coverage

| Test | File | Purpose |
|------|------|---------|
| CB-2 | `chatbot_tests.py` | System prompt validation (20 questions) |
| CB-8 | `chatbot_tests.py` | Scope enforcement (10 off-topic refusals) |
| CB-9 | `chatbot_tests.py` | Response quality (16/20 correctness) |
| CB-12 | `test_cb12_feedback.py` | Feedback persistence and upserts |
| CB-16 | `chatbot_tests.py` | Symbolic math verification |

### GitHub Actions Workflow (CB-22)

- **On Every PR**: Run mock tests (Python 3.11, 3.12)
- **Nightly (2 AM UTC)**: Run against real Grok API with secret key
- **Thresholds**:
  - CB-8: Must pass 10/10 scope tests
  - CB-9: Must pass 16/20 correctness tests
  - Workflow fails if thresholds not met

---

## 👨‍💻 Development

### Adding a New Feature

1. **Write tests first** (TDD):
   - Add test cases to `aiService/tests/chatbot_tests.py` or new test file
   - Use `USE_MOCK=True` during development

2. **Implement in AI Service** (`aiService/services/llm_client.py`):
   - Add logic to system prompt or message building
   - Update `_build_messages()` if needed

3. **Wire through Backend** (`backend/app/routes/chat.py`):
   - Fetch/store data from database
   - Pass parameters to AI service
   - Return metadata in response

4. **Update Frontend** (`frontend/src/components/` and `frontend/src/services/`):
   - Add UI components or interactions
   - Update `chatApi.js` functions to handle new fields
   - Display new data in components

5. **Run tests**:
   ```bash
   USE_MOCK=True python -m aiService.tests.chatbot_tests
   ```

### Code Style

- **Python**: PEP 8 (black, flake8)
- **JavaScript**: ESLint + Prettier (from `frontend/package.json`)
- **Database**: Use parameterized queries to prevent SQL injection

### Database Migrations

New tables are auto-created on first run via `app.database.db.init_db()`. To modify schema:

1. Update `SCHEMA` in `backend/app/database/db.py`
2. Delete `backend/app/database/calcvoyager.db` (dev only)
3. Backend will recreate on next run

---

## 🐛 Troubleshooting

### "Could not reach the chat service"
- Ensure AI Service is running on port 8001
- Check `REACT_APP_API_URL` in frontend `.env`

### "Authentication failed" / "GROK_API_KEY invalid"
- Verify key in `aiService/services/.env`
- Check key hasn't expired on xAI dashboard
- Set `USE_MOCK=True` to bypass API during development

### Rate limit exceeded (429)
- Authenticated users: wait until next day (reset at UTC midnight)
- Guests: wait 1 hour (session window)
- Adjust limits in `backend/app/routes/chat.py` RateLimiter class

### Test failures in mock mode
- Expected: Mock responses lack LaTeX formatting → tests show 0/20 passing
- Workaround: Run with real API (`USE_MOCK=False`) for full validation

### Session export empty
- Ensure session has at least one assistant message
- Check `chat_messages` table has data for the session

---

## 📦 Dependencies

### Core

| Package | Version | Purpose |
|---------|---------|---------|
| `starlette` | Latest | Backend web framework |
| `fastapi` | Latest | AI service framework |
| `openai` | Latest | xAI Grok client |
| `aiosqlite` | Latest | Async SQLite |
| `sympy` | Latest | Symbolic math verification |
| `react` | 18+ | Frontend UI |
| `katex` | Latest | Math rendering |

See `aiService/requirements.txt` and `backend/requirements.txt` for full lists.

---

## 📄 License

Proprietary — Quantum Logics

---

## 👥 Authors

- **Team Theta** — System prompt design (Cal personality)
- **CalcVoyager Team** — Full stack development

---

## 🔗 Related Documentation

- [AI Service README](aiService/readme.md) — Detailed LLM configuration
- [Testing README](aiService/tests/README_TESTING.md) — Test suite guide
- [GitHub Actions Workflow](.github/workflows/tests.yml) — CI/CD pipeline

---

## ✅ Recent Updates (Latest Build)

### Fixed Bugs
- ✅ **CB-13**: Fixed critical NameError in session summarization (undefined `session_id` and `client`)
- ✅ **CB-13**: Wired session summary into LLM calls as system-level context
- ✅ **CB-12**: Completed frontend feedback UI → backend persistence flow
- ✅ **CB-11/CB-14**: Implemented rate limiting with 429 handling
- ✅ **CB-16**: Extended symbolic verification to multivariable expressions
- ✅ **CB-22**: Added GitHub Actions workflow with mock and nightly real-API tests

### Features Completed
- 🎯 Multivariable calculus support (partial derivatives)
- 🎯 Graceful error handling for unsupported operations
- 🎯 Full feedback→difficulty→adaptation loop
- 🎯 CI/CD pipeline with threshold enforcement
