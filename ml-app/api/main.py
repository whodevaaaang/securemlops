"""FastAPI service that exposes the sentiment model behind /predict."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from .model_loader import load_or_train

API_TOKEN_ENV = "API_TOKEN"
MODEL_PATH = Path(__file__).resolve().parent.parent / "model" / "artifacts" / "model.joblib"
APP_VERSION = "1.0.0"

app = FastAPI(
    title="SecureMLOps Sentiment API",
    version=APP_VERSION,
    description="Serves a sentiment classifier behind a hardened CI/CD pipeline.",
)

_model = load_or_train(MODEL_PATH)
_started_at = time.time()


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    token: str | None = Field(default=None, description="Optional API token; required if API_TOKEN is set.")


class PredictResponse(BaseModel):
    label: str
    score: float
    model_version: str


class HealthResponse(BaseModel):
    status: str
    uptime_seconds: float
    model_loaded: bool
    version: str


def _check_token(provided: str | None) -> None:
    expected = os.environ.get(API_TOKEN_ENV)
    if not expected:
        return
    if provided != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API token")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        uptime_seconds=time.time() - _started_at,
        model_loaded=_model is not None,
        version=APP_VERSION,
    )


@app.get("/ready")
def ready() -> dict:
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"ready": True}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    _check_token(request.token)
    proba: List[float] = _model.predict_proba([request.text])[0].tolist()
    positive_score = float(proba[1])
    label = "positive" if positive_score >= 0.5 else "negative"
    return PredictResponse(label=label, score=positive_score, model_version=APP_VERSION)
