import os

from fastapi.testclient import TestClient

from app.main import app


class StubResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError("request failed")

    def json(self):
        return self._payload


def test_ai_health_endpoint_returns_ok():
    client = TestClient(app)
    response = client.get("/api/ai/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ai_chat_endpoint_requires_authentication():
    client = TestClient(app)
    response = client.post(
        "/api/ai/chat",
        json={"message": "Hello"},
    )

    assert response.status_code == 401


def test_ai_chat_uses_structured_response_when_configured(monkeypatch):
    import app.main as main

    class FakeHTTPXResponse:
        def __init__(self, payload):
            self._payload = payload
            self.status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class FakeClient:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def post(self, *args, **kwargs):
            return FakeHTTPXResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": '{"reply": "Done", "update_board": true, "board_update": {"columns": [], "cards": {}}}'
                            }
                        }
                    ]
                }
            )

    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(main.httpx, "Client", FakeClient)

    client = TestClient(app)
    response = client.post(
        "/api/ai/chat",
        json={"message": "Hello"},
        headers={"Authorization": "Bearer token-user"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["reply"] == "Done"
    assert payload["update_board"] is True
    assert payload["board_update"] == {"columns": [], "cards": {}}


def test_ai_chat_moves_a_card_to_done_when_requested(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    client = TestClient(app)
    response = client.post(
        "/api/ai/chat",
        json={
            "message": "move the card to done",
            "board": {
                "columns": [
                    {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]},
                    {"id": "col-done", "title": "Done", "cardIds": []},
                ],
                "cards": {
                    "card-1": {"id": "card-1", "title": "Draft scope", "details": "Capture the first priorities."}
                },
            },
        },
        headers={"Authorization": "Bearer token-user"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["update_board"] is True
    assert payload["board_update"]["columns"][1]["cardIds"] == ["card-1"]
    assert payload["board_update"]["columns"][0]["cardIds"] == []
