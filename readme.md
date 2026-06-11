
# Language App Backend (FastAPI + LLM + PostgreSQL)

A FastAPI backend that generates language learning flashcards using an LLM, stores them in PostgreSQL, and uses a cache-first strategy to avoid redundant API calls.



## System design

```text
React + TypeScript frontend
        ↓
     FastAPI backend
        ↓
 PostgreSQL cache/store
        ↓
   LLM provider API
```

That gives a much better separation:

* frontend only worries about UI
* backend owns business logic
* DB/cache logic stays server-side
* API key never touches the browser
---

## ✨ Features

* Generate flashcards from:

  * Phrase list
  * Topic + difficulty
* Multiple-choice questions with distractors
* Cache-first lookup (DB → LLM fallback)
* Automatic schema creation
* Built-in Swagger UI (`/docs`)
* Clean service + repository architecture

---

## 🧱 Tech Stack

* FastAPI
* Uvicorn
* psycopg (v3)
* PostgreSQL
* OpenAI API

---

## 📁 Project Structure

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── flashcards.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── connection.py
│   │   └── schema.py
│   ├── models/
│   │   ├── requests.py
│   │   └── responses.py
│   ├── repositories/
│   │   └── flashcard_repository.py
│   ├── services/
│   │   ├── llm_service.py
│   │   └── flashcard_service.py
│   └── prompts/
│       ├── make_flashcard_for_phrase.txt
│       └── make_flashcard_for_topic.txt
└── .env
```

---

## ⚙️ Setup

### 1. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

---

### 2. Install dependencies

```bash
pip install fastapi uvicorn psycopg openai python-dotenv
```

---

### 3. Setup PostgreSQL

Make sure PostgreSQL is running locally.

Create a database:

```sql
CREATE DATABASE language_db;
```

---

### 4. Create `.env`

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini
DATABASE_URL=postgresql://postgres:password@localhost:5432/language_db
```

---

## ▶️ Run the server

```bash
uvicorn app.main:app --reload
```

---

## 🌐 API Docs (Swagger)

Open in browser:

```text
http://127.0.0.1:8000/docs
```

---

## 🔌 API Endpoints

### 1. Phrase Flashcard

**POST** `/api/flashcards/phrase`

```json
{
  "source_items": ["守株待兔", "杞人忧天"],
  "source_language": "Chinese",
  "target_language": "English",
  "num_options": 4,
  "text_type": "idiom"
}
```

👉 Returns **ONE** flashcard (cache-first)

---

### 2. Topic Flashcard

**POST** `/api/flashcards/topic`

```json
{
  "topic": "classical literature",
  "difficulty": "advanced",
  "source_language": "Chinese",
  "target_language": "English",
  "num_options": 4,
  "text_type": "phrase"
}
```

---

## 🧠 How It Works

```text
Request
  ↓
Check DB (cache)
  ↓
Hit → return immediately
Miss → call LLM
  ↓
Sanitize response
  ↓
Save to PostgreSQL
  ↓
Return result
```

---

## ⚡ Notes

* Tables are created automatically on first request
* Responses include:

  * `cache_hit: true | false`
* Only **one flashcard** is returned per request (by design)
* LLM output is sanitized before parsing

---

## 🧪 Example Response

```json
{
  "source_language": "Chinese",
  "target_language": "English",
  "prompt_type": "phrase",
  "text_type": "idiom",
  "difficulty": "intermediate",
  "topic": null,
  "source_text": "守株待兔",
  "target_text": "To wait for a windfall",
  "explanation": "...",
  "options": [
    "To wait for a windfall",
    "To catch rabbits",
    "To farm diligently",
    "To be careful and observant"
  ],
  "cache_hit": false
}
```

---

## 🚀 Next Steps

* Add frontend (React + TypeScript)
* Add request hashing for stronger caching
* Add validation layer for LLM output
* Add user progress tracking



# Docker setup


Below is a copy-ready Docker setup.

## Project root structure

```text
project-root/
  .env
  docker-compose.yml
  reverse-proxy/
    nginx.conf
  language-app-backend/
    Dockerfile
    .dockerignore
    .env
    requirements.txt
  language-app-frontend/
    Dockerfile
    .dockerignore
    nginx.conf.template
    .env
```

## Root `.env`

```env
BACKEND_PORT=8000
FRONTEND_PORT=5173

DB_NAME=language_db
DB_USER=postgres
DB_PASSWORD=mypw

API_ROOT_PATH=/language-app-api
FRONTEND_BASE_PATH=/language-app-web/
```


## `language-app-backend/.env`

```env
PORT=8000

DATABASE_URL=postgresql://postgres:mypw@db:5432/language_db

API_ROOT_PATH=/language-app-api
APP_BASE_URL=http://localhost:8000/language-app-api
FRONTEND_BASE_URL=http://localhost:8000/language-app-web/
GOOGLE_REDIRECT_URI=http://localhost:8000/language-app-api/auth/google/callback

SESSION_COOKIE_NAME=language_app_session
SESSION_TTL_DAYS=30
STARLETTE_SESSION_SECRET=change_this_to_a_long_random_secret
SESSION_SAME_SITE=lax
SESSION_HTTPS_ONLY=false

CORS_ALLOW_ORIGINS=http://localhost:8000,http://127.0.0.1:8000

OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL_NAME=gpt-4o-mini

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

## `language-app-frontend/.env`

```env
PORT=5173
VITE_APP_BASE_PATH=/language-app-web/
VITE_API_BASE_URL=http://localhost:8000/language-app-api
```

## Required code settings

Backend `app/main.py` should use:

```python
app = FastAPI(
    title=settings.app_name,
    root_path=settings.api_root_path if settings.api_root_path != "/" else "",
)
```

Frontend `vite.config.ts` should use:

```ts
base: env.VITE_APP_BASE_PATH || "/",
```

Frontend `App.tsx` should use:

```tsx
const basePath = (import.meta.env.VITE_APP_BASE_PATH || "/").replace(/\/+$/, "");

<BrowserRouter basename={basePath}>
```

## Run

From `project-root`:

```bash
docker compose up --build
```

Open:

```text
http://localhost:8000/language-app-web/
```

Backend Swagger:

```text
http://localhost:8000/language-app-api/docs
```

## Google OAuth redirect URI

Add this in Google Cloud Console:

```text
http://localhost:8000/language-app-api/auth/google/callback
```


