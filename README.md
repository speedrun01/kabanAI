# Project Management MVP

A local Kanban board app with a simple login flow, board persistence, and an AI assistant sidebar.

## Requirements

- Docker Desktop
- Node.js 20+
- Python 3.11+

## Run locally

### 1. Start the app with the provided script

From the project root:

```bash
./scripts/start.sh
```

This starts the app stack with the backend API and the frontend.

If you want to stop it later, run:

```bash
./scripts/stop.sh
```

### 2. Open the app

Open:

- Frontend: http://localhost:3001
- Backend health check: http://localhost:8001/health

### 3. Sign in

Use:

- Username: user
- Password: password

## Run frontend manually

If you want to run the frontend directly:

```bash
cd frontend
npm install
npm run dev
```

The app will be available at http://localhost:3001.

## Run backend manually

If you want to run the backend directly:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

The backend will be available at http://localhost:8001.

## Environment

The backend reads the OpenRouter API key from the project root .env file.

## Tests

### Frontend

```bash
cd frontend
npm run test:unit
```

### Backend

```bash
cd backend
python3 -m pytest -q tests/test_ai.py
```
