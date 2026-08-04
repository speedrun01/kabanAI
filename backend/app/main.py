from pathlib import Path
from typing import Any

import json
import os

import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(title="Project Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict[str, str]


class BoardPayload(BaseModel):
    columns: list[dict[str, Any]] = Field(default_factory=list)
    cards: dict[str, Any] = Field(default_factory=dict)


class AIChatRequest(BaseModel):
    message: str
    history: list[dict[str, str]] = Field(default_factory=list)
    board: dict[str, Any] = Field(default_factory=dict)


class AIChatResponse(BaseModel):
    reply: str
    update_board: bool = False
    board_update: BoardPayload = None


DEFAULT_BOARD = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]},
        {"id": "col-done", "title": "Done", "cardIds": []},
    ],
    "cards": {
        "card-1": {"id": "card-1", "title": "Draft scope", "details": "Capture the first priorities."},
    },
}


users_db: dict[str, dict[str, str]] = {"user": {"password": "password"}}
boards_db: dict[str, dict[str, Any]] = {}


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def landing_page():
    return """
    <html>
      <head><title>Project Management MVP</title></head>
      <body>
        <h1>Hello World</h1>
        <p>The backend scaffold is running.</p>
      </body>
    </html>
    """


@app.get("/api/hello")
def hello_api():
    return {"message": "Hello from the backend"}


@app.post("/api/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    user = users_db.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = f"token-{payload.username}"
    return {"token": token, "user": {"username": payload.username}}


def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    token = authorization.split(" ", 1)[1]
    if token.startswith("token-"):
        username = token.split("-", 1)[1]
        if username in users_db:
            return username

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


@app.get("/api/board")
def get_board(username: str = Depends(get_current_user)):
    del username
    return boards_db.setdefault("user", DEFAULT_BOARD.copy())


@app.put("/api/board")
def save_board(payload: BoardPayload, username: str = Depends(get_current_user)):
    del username
    boards_db["user"] = payload.model_dump()
    return boards_db["user"]


@app.get("/api/ai/health")
def ai_health():
    return {"status": "ok"}


def infer_board_update(message: str, board_payload: dict[str, Any]) -> dict[str, Any] | None:
    normalized_message = message.lower()
    if "move" not in normalized_message and "done" not in normalized_message and "completed" not in normalized_message:
        return None

    columns = board_payload.get("columns", [])
    cards = board_payload.get("cards", {})
    if not columns or not cards:
        return None

    target_column = None
    for column in columns:
        title = str(column.get("title", "")).lower()
        if title in {"done", "completed", "finished"}:
            target_column = column
            break

    if not target_column:
        return None

    source_card_id = None
    source_column = None
    for column in columns:
        if column.get("id") == target_column.get("id"):
            continue
        for card_id in column.get("cardIds", []):
            if card_id in cards:
                source_card_id = card_id
                source_column = column
                break
        if source_card_id:
            break

    if not source_card_id or not source_column:
        return None

    target_card = cards.get(source_card_id, {})
    card_title = str(target_card.get("title", "the card"))

    next_columns = []
    for column in columns:
        if column.get("id") == source_column.get("id"):
            next_columns.append(
                {
                    **column,
                    "cardIds": [card_id for card_id in column.get("cardIds", []) if card_id != source_card_id],
                }
            )
        elif column.get("id") == target_column.get("id"):
            next_columns.append(
                {
                    **column,
                    "cardIds": [*column.get("cardIds", []), source_card_id],
                }
            )
        else:
            next_columns.append(column)

    return {
        "reply": f"Moved {card_title} to Done.",
        "board_update": {"columns": next_columns, "cards": cards},
    }


@app.post("/api/ai/chat", response_model=AIChatResponse)
def ai_chat(payload: AIChatRequest, username: str = Depends(get_current_user)):
    del username
    board_payload = payload.board or {
        "columns": DEFAULT_BOARD["columns"],
        "cards": DEFAULT_BOARD["cards"],
    }

    fallback_update = infer_board_update(payload.message, board_payload)
    if fallback_update:
        return AIChatResponse(
            reply=fallback_update["reply"],
            update_board=True,
            board_update=fallback_update["board_update"],
        )

    if not os.getenv("OPENROUTER_API_KEY"):
        return AIChatResponse(
            reply="AI is not configured yet. Please set OPENROUTER_API_KEY to enable chat.",
            update_board=False,
        )

    try:
        request_body = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a Kanban assistant. Respond briefly and return JSON with "
                        "reply, update_board, and board_update."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Current board: {board_payload}\n"
                        f"User request: {payload.message}\n"
                        f"History: {payload.history}"
                    ),
                },
            ],
        }
        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    "Content-Type": "application/json",
                },
                json=request_body,
            )
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:-3].strip()
            parsed = json.loads(content)
            reply = parsed.get("reply", "I can help with that.")
            update_board = bool(parsed.get("update_board", False))
            board_update = parsed.get("board_update")
            if update_board and board_update:
                return AIChatResponse(reply=reply, update_board=update_board, board_update=board_update)
            fallback_update = infer_board_update(payload.message, board_payload)
            if fallback_update:
                return AIChatResponse(
                    reply=fallback_update["reply"],
                    update_board=True,
                    board_update=fallback_update["board_update"],
                )
            return AIChatResponse(reply=reply, update_board=update_board, board_update=board_update)
    except Exception:
        fallback_update = infer_board_update(payload.message, board_payload)
        if fallback_update:
            return AIChatResponse(
                reply=fallback_update["reply"],
                update_board=True,
                board_update=fallback_update["board_update"],
            )
        return AIChatResponse(
            reply="The AI request failed. Please try again in a moment.",
            update_board=False,
        )
