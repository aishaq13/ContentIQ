from fastapi.testclient import TestClient

from app.main import app


def test_metadata_round_trip() -> None:
    with TestClient(app) as client:
        create = client.post(
            "/api/v1/metadata",
            json={"key": "doc-1", "value": {"status": "active"}, "tags": ["gold"]},
        )
        assert create.status_code == 201
        assert create.json()["version"] == 1

        fetch = client.get("/api/v1/metadata/doc-1")
        assert fetch.status_code == 200
        assert fetch.json()["key"] == "doc-1"

        listing = client.get("/api/v1/metadata")
        assert listing.status_code == 200
        assert len(listing.json()) >= 1
