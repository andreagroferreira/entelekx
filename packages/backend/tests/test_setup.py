"""Tests for setup endpoints."""

import pytest
from fastapi.testclient import TestClient

from entelekx_backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_validate_database_sqlite(client: TestClient, tmp_path):
    db = tmp_path / "setup_validate.db"
    response = client.post(
        "/api/v1/setup/validate-database", json={"url": f"sqlite+aiosqlite:///{db}"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["backend"] == "sqlite"
    assert "successful" in body["message"]


def test_validate_database_postgres_string(client: TestClient):
    # Postgres URL with asyncpg driver; actual connectivity is not exercised.
    response = client.post(
        "/api/v1/setup/validate-database",
        json={"url": "postgresql+asyncpg://localhost/entelekx_test"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["backend"] == "postgres"


def test_initialize_sqlite(client: TestClient, tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    db_path = tmp_path / "setup_init.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"

    # Isolate wizard env file so it does not overwrite developer .env
    monkeypatch.setattr(
        "entelekx_backend.core.config.get_settings",
        lambda: type(
            "Settings",
            (),
            {
                "data_dir": data_dir,
                "resolved_database_url": db_url,
                "version": "0.1.0",
            },
        )(),
    )

    response = client.post(
        "/api/v1/setup/initialize",
        json={
            "database_url": db_url,
            "admin_username": "admin",
            "admin_password": "strong-pass",
            "backup_enabled": True,
            "backup_path": str(data_dir / "backups"),
            "backup_frequency": "daily",
            "backup_encrypted": True,
            "default_provider": "openrouter",
        },
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "initialized"
    assert body["admin_username"] == "admin"
    assert body["backup_enabled"] is True

    # Idempotent: second initialize should succeed without error
    response2 = client.post(
        "/api/v1/setup/initialize",
        json={
            "database_url": db_url,
            "admin_username": "admin",
            "admin_password": "different",
            "backup_enabled": False,
        },
    )
    assert response2.status_code == 200


def test_initialize_invalid_database_url(client: TestClient):
    response = client.post(
        "/api/v1/setup/initialize",
        json={
            "database_url": "postgresql://127.0.0.1:1/entelekx_nonexistent",
            "admin_username": "admin",
            "admin_password": "strong-pass",
        },
    )
    assert response.status_code == 400


def test_backup_validate_path(client: TestClient, tmp_path):
    backup_path = tmp_path / "backups"
    response = client.post("/api/v1/setup/backup", json={"path": str(backup_path)})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["archive_path"] == str(backup_path / "entelekx_backup_test.zip")


def test_backup_invalid_path(client: TestClient):
    response = client.post("/api/v1/setup/backup", json={"path": "/nonexistent/readonly/location"})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is False
    assert "not writable" in body["message"]
