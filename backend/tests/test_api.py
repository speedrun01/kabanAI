from fastapi.testclient import TestClient

from app.main import app


def test_login_returns_token_for_valid_credentials():
    client = TestClient(app)
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )

    assert response.status_code == 200
    assert "token" in response.json()
    assert response.json()["user"]["username"] == "user"


def test_board_is_created_and_persisted_for_authenticated_user():
    client = TestClient(app)
    login_response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )
    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    initial_response = client.get("/api/board", headers=headers)
    assert initial_response.status_code == 200
    assert initial_response.json()["columns"][0]["title"] == "Backlog"

    board_payload = {
        "columns": [
            {"id": "col-1", "title": "Ready", "cardIds": ["card-1"]},
            {"id": "col-2", "title": "Done", "cardIds": []},
        ],
        "cards": {
            "card-1": {"id": "card-1", "title": "Ship it", "details": "Done"},
        },
    }

    save_response = client.put("/api/board", headers=headers, json=board_payload)
    assert save_response.status_code == 200

    load_response = client.get("/api/board", headers=headers)
    assert load_response.status_code == 200
    assert load_response.json()["columns"][0]["title"] == "Ready"
    assert load_response.json()["cards"]["card-1"]["title"] == "Ship it"
