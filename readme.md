## Backend: `language-app-api`

**Tech:** FastAPI + PostgreSQL + psycopg 3


```text
language-app-api/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── flashcards.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── db/
│   │   ├── connection.py
│   │   └── schema.sql
│   ├── models/
│   │   ├── requests.py
│   │   └── responses.py
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── flashcard_service.py
│   │   └── cache_service.py
│   ├── repositories/
│   │   └── flashcard_repository.py
│   └── prompts/
│       ├── make_flashcard_for_phrase.txt
│       └── make_flashcard_for_topic.txt
├── tests/
├── .env
├── requirements.txt
└── README.md
```

### Backend responsibilities

* expose REST endpoints
* validate request payloads
* check DB cache first
* call LLM on cache miss
* save and return structured flashcards

### Good first endpoints

* `POST /api/flashcards/phrase`
* `POST /api/flashcards/topic`
* `GET /api/flashcards/{flashcard_id}`
* `GET /api/health`

### Example request models

For phrase:

```json
{
  "source_items": ["守株待兔", "杞人忧天"],
  "source_language": "Chinese",
  "target_language": "English",
  "num_options": 4,
  "text_type": "idiom"
}
```

For topic:

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


