"""Offline HTTP API contract tests; real model calls are replaced with a test double."""

from fastapi.testclient import TestClient
from types import SimpleNamespace
import pytest
import main

client = TestClient(main.app)


class FakeClassifier:
    def __call__(self, text, **kwargs):
        label = "NEGATIVE" if "terrible" in text.lower() else "POSITIVE"
        return [{"label": label, "score": 0.95}]


@pytest.fixture(autouse=True)
def mock_hugging_face_model(monkeypatch):
    def fake_pipeline():
        return FakeClassifier()
    fake_pipeline.cache_info = lambda: SimpleNamespace(currsize=0)
    monkeypatch.setattr(main, "get_sentiment_pipeline", fake_pipeline)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"
    assert response.json()["model"] == main.MODEL_ID


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert isinstance(response.json()["model_loaded"], bool)


def test_positive():
    response = client.post("/predict", json={"text": "I love this movie"})
    assert response.status_code == 200
    assert response.json() == {"label": "POSITIVE", "score": 0.95, "model": main.MODEL_ID}


def test_negative():
    response = client.post("/predict", json={"text": "A terrible experience"})
    assert response.status_code == 200
    assert response.json()["label"] == "NEGATIVE"


def test_strip_whitespace():
    response = client.post("/predict", json={"text": "  Great  "})
    assert response.status_code == 200


@pytest.mark.parametrize("payload", [{}, {"text": ""}, {"text": "     "}, {"text": 123}, {"text": "a" * 2001}])
def test_invalid_inputs(payload):
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_malformed_json():
    response = client.post("/predict", content="not JSON", headers={"content-type": "application/json"})
    assert response.status_code == 422


def test_inference_error(monkeypatch):
    def fail():
        raise RuntimeError("model files unavailable")
    monkeypatch.setattr(main, "get_sentiment_pipeline", fail)
    response = client.post("/predict", json={"text": "test"})
    assert response.status_code == 503
    assert "detail" in response.json()
    assert "model files unavailable" not in response.text
