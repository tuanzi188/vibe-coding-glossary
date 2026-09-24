"""行程接口的最小回归测试。"""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """每个测试使用独立的临时 SQLite 文件。"""

    database_path = tmp_path / "test.db"
    monkeypatch.setenv("TRIP_DB_PATH", str(database_path))
    from backend.app import database

    database.DB_PATH = database_path
    from backend.app.main import app

    with TestClient(app) as test_client:
        yield test_client


def test_list_trips_returns_seed_data(client: TestClient) -> None:
    response = client.get("/api/trips")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3


def test_filter_trips_by_status(client: TestClient) -> None:
    response = client.get("/api/trips", params={"status": "planned"})
    assert response.status_code == 200
    assert response.json()["items"][0]["destination"] == "杭州"


def test_create_and_delete_trip(client: TestClient) -> None:
    created = client.post(
        "/api/trips",
        json={
            "title": "厦门海边行",
            "destination": "厦门",
            "days": 3,
            "budget": 2600,
            "status": "draft",
        },
    )
    assert created.status_code == 201
    trip_id = created.json()["id"]
    deleted = client.delete(f"/api/trips/{trip_id}")
    assert deleted.status_code == 204
