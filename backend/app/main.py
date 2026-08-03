from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Project Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
