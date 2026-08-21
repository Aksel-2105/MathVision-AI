from datetime import datetime

from fastapi.testclient import TestClient


def test_health_contract(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["phase"] == "foundation"
    assert payload["service"] == "MathVision AI API"
    timestamp = datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    assert isinstance(timestamp, datetime)


def test_unknown_route_is_not_hidden(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")

    assert response.status_code == 404


def test_api_responses_include_security_headers(client: TestClient) -> None:
    response = client.get("/api/v1/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["cache-control"] == "no-store"
