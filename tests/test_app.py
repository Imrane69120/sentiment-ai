"""Tests pour l'API Flask src/app.py"""

import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealth:
    def test_health_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"


class TestAnalyzeEndpoint:
    def test_positive(self, client):
        resp = client.post("/analyze", json={"text": "super excellent"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["label"] == "positive"

    def test_negative(self, client):
        resp = client.post("/analyze", json={"text": "horrible terrible"})
        assert resp.status_code == 200
        assert resp.get_json()["label"] == "negative"

    def test_missing_text(self, client):
        resp = client.post("/analyze", json={})
        assert resp.status_code == 400
        assert "error" in resp.get_json()

    def test_no_body(self, client):
        resp = client.post("/analyze")
        assert resp.status_code in (400, 415)


class TestBatchEndpoint:
    def test_batch_basic(self, client):
        resp = client.post("/batch", json={"texts": ["super", "horrible"]})
        assert resp.status_code == 200
        data = resp.get_json()
        assert "results" in data
        assert "summary" in data
        assert len(data["results"]) == 2

    def test_batch_missing_texts(self, client):
        resp = client.post("/batch", json={})
        assert resp.status_code == 400

    def test_batch_no_body(self, client):
        resp = client.post("/batch")
        assert resp.status_code in (400, 415)
