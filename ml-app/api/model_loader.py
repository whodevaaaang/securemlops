"""Loads the persisted model, training on the fly if no artifact exists."""

from __future__ import annotations

import sys
from pathlib import Path

import joblib

ML_APP_ROOT = Path(__file__).resolve().parent.parent
if str(ML_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_APP_ROOT))


def load_or_train(model_path: Path):
    if model_path.exists():
        return joblib.load(model_path)
    from model.train import build_pipeline, TRAIN_LABELS, TRAIN_TEXTS

    pipeline = build_pipeline()
    pipeline.fit(TRAIN_TEXTS, TRAIN_LABELS)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    return pipeline
