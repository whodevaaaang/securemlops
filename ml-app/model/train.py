"""Train a small sentiment classifier and persist it as artifacts/model.joblib."""
from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ARTIFACT_DIR = Path(__file__).parent / "artifacts"
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = ARTIFACT_DIR / "model.joblib"

TRAIN_TEXTS = [
    "this product is amazing and I love it",
    "fantastic quality, highly recommend to everyone",
    "best purchase I have made this year",
    "absolutely wonderful experience, will buy again",
    "great value for money, very satisfied",
    "exceeded my expectations, perfect",
    "delightful and well crafted",
    "happy with the service and the product",
    "terrible product, completely broken",
    "worst experience ever, do not buy",
    "awful quality and rude support",
    "totally disappointed, waste of money",
    "horrible, returned it the same day",
    "bad packaging and damaged on arrival",
    "regret buying this, very poor",
    "frustrating and useless",
]
TRAIN_LABELS = [1] * 8 + [0] * 8


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("clf", LogisticRegression(max_iter=200, random_state=42)),
        ]
    )


def main() -> None:
    pipeline = build_pipeline()
    pipeline.fit(TRAIN_TEXTS, TRAIN_LABELS)
    accuracy = pipeline.score(TRAIN_TEXTS, TRAIN_LABELS)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH} (train accuracy={accuracy:.3f})")


if __name__ == "__main__":
    main()
