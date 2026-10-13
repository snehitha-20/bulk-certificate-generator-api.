
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import sqlite3

import main


@pytest.fixture
def client(monkeypatch):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Use a separate database for testing
        test_db = temp_path / "test_certificates.db"
        test_output = temp_path / "generated_certificates"
        test_output.mkdir()

        monkeypatch.setattr(main, "DB_PATH", test_db)
        monkeypatch.setattr(main, "OUTPUT_DIR", test_output)

        main.init_db()

        with TestClient(main.app) as test_client:
            yield test_client


def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "Bulk Certificate Generator API is running"
    )


def test_create_job(client):
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-13",
            "recipients": [
                {
                    "name": "Ananya Sharma",
                    "email": "ananya@example.com",
                }
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["status"] == "COMPLETED"
    assert data["total"] == 1
    assert data["succeeded"] == 1
    assert data["failed"] == 0
    assert len(data["certificates"]) == 1


def test_invalid_email(client):
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-13",
            "recipients": [
                {
                    "name": "Ananya Sharma",
                    "email": "not-an-email",
                }
            ],
        },
    )

    assert response.status_code == 422


def test_empty_recipients(client):
    response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-13",
            "recipients": [],
        },
    )

    assert response.status_code == 422


def test_unknown_job(client):
    response = client.get("/jobs/invalid-job-id")

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_list_jobs(client):
    response = client.get("/jobs")

    assert response.status_code == 200
    assert response.json()["total_jobs"] == 0
    assert response.json()["jobs"] == []


def test_download_certificate(client):
    create_response = client.post(
        "/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-13",
            "recipients": [
                {
                    "name": "Ananya Sharma",
                    "email": "ananya@example.com",
                }
            ],
        },
    )

    certificate_id = create_response.json()["certificates"][0][
        "certificate_id"
    ]

    response = client.get(
        f"/certificates/{certificate_id}/download"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_unknown_certificate(client):
    response = client.get(
        "/certificates/invalid-certificate-id/download"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Certificate not found"