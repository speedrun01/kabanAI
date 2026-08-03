from fastapi.testclient import TestClient

from app.main import app


def test_healthcheck_returns_ok():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_serves_hello_world_page():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Hello World" in response.text


def test_api_hello_returns_message():
    client = TestClient(app)
    response = client.get("/api/hello")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello from the backend"}
