"""Integration tests for the FastAPI service."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent))

from ml_app_pkg import app  # noqa: E402  (set up via conftest)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_ready_endpoint(client: TestClient) -> None:
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json() == {"ready": True}


def test_predict_positive(client: TestClient) -> None:
    response = client.post("/predict", json={"text": "absolutely fantastic, I love it"})
    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "positive"
    assert 0.5 <= body["score"] <= 1.0


def test_predict_negative(client: TestClient) -> None:
    response = client.post("/predict", json={"text": "terrible awful waste of money"})
    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "negative"
    assert 0.0 <= body["score"] < 0.5


def test_predict_rejects_blank(client: TestClient) -> None:
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422


def test_predict_requires_token_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_TOKEN", "secret-token")
    from importlib import reload

    import ml_app_pkg

    reload(ml_app_pkg)
    client = TestClient(ml_app_pkg.app)
    bad = client.post("/predict", json={"text": "great", "token": "wrong"})
    good = client.post("/predict", json={"text": "great", "token": "secret-token"})
    assert bad.status_code == 401
    assert good.status_code == 200
    monkeypatch.delenv("API_TOKEN", raising=False)
    reload(ml_app_pkg)
