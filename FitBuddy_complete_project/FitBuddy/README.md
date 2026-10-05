# FitBuddy – AI Fitness Plan Generator

A complete FastAPI + Jinja2 + SQLite + Gemini application based on the supplied FitBuddy specification.

## Features
- User form: name, user ID, age, weight, goal, intensity
- AI-generated 7-day workout plan
- AI nutrition/recovery tip
- Feedback-based plan revision
- SQLite persistence with SQLAlchemy
- Admin/coach view at `/view-all-users`
- REST API plus HTML UI
- Local demo fallback when no Gemini API key is configured
- Automated tests

## Setup

### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

### Windows CMD
```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Put your Gemini API key in `.env` if you want live Gemini responses. If the key is blank, the complete application still works using a clearly labeled local demo generator.

## Run

```bash
python -m uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/view-all-users

## Test

```bash
pytest -q
```

## API

`GET /api/health`

`POST /api/plans`
```json
{
  "name": "Demo User",
  "user_id": "demo001",
  "age": 20,
  "weight": 60,
  "goal": "general wellness",
  "intensity": "medium"
}
```

`POST /api/plans/{user_id}/feedback`
```json
{
  "feedback": "Add more cardio and keep one full recovery day."
}
```

`GET /api/users`

`DELETE /api/users/{user_id}`

## Structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   ├── gemini_generator.py
│   ├── gemini_flash_generator.py
│   ├── updated_plan.py
│   └── services/ai_service.py
├── templates/
├── static/css/
├── static/js/
├── tests/
├── data/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Note
This is a wellness-planning demonstration, not medical advice. The AI prompts explicitly avoid diagnosis, extreme dieting, unsafe exercise, and guaranteed outcomes.
