"""
Training script for SkyGuard AI's two models:

  1. IsolationForest      - unsupervised anomaly detector
  2. RandomForestClassifier - supervised fault-type classifier

This trains the models ONCE, on the default simulation configuration
(seed=42, 500 rows, default fault injection, contamination=0.08 - the
same defaults the original prototype's sidebar starts with), and saves
them to ml/models/ so the backend never has to retrain on startup.

Run:
    python -m ml.training.train

IMPORTANT - read before assuming this is the whole story:
This app is a live "what-if" simulator: the sidebar/UI lets a person
change the random seed, the contamination rate and the fault-injection
parameters, which changes the *dataset itself* and therefore the correct
IsolationForest contamination and the correct Random Forest ground-truth
labels. That behavior is inherent to the original prototype (Streamlit
reran and refit both models on every widget change). To preserve that
exact functionality unchanged, ml/prediction/predict.py refits both
models live whenever a request's parameters differ from these persisted
defaults, and only uses this persisted pair as a fast path when the
request matches the default configuration exactly. See ml/prediction/predict.py
and the project README for details.
"""

import os
import sys

import joblib
from sklearn.ensemble import IsolationForest, RandomForestClassifier

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ml.datasets.generate_synthetic import generate_weather_data
from ml.preprocessing.features import (
    CLF_FEATURE_COLUMNS,
    ISO_FEATURE_COLUMNS,
    extract_sensor_features,
)

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

# Same defaults as the original prototype's sidebar.
DEFAULT_PARAMS = dict(
    rows=500,
    seed=42,
    spike_en=True, spike_t=95.0, spike_idx=120,
    frozen_en=True, frozen_dur=15, frozen_idx=240,
    drift_en=True, drift_dur=30, drift_idx=360,
)
DEFAULT_CONTAMINATION = 0.08


def train_and_save(params: dict = DEFAULT_PARAMS, contamination: float = DEFAULT_CONTAMINATION) -> dict:
    os.makedirs(MODELS_DIR, exist_ok=True)

    df = generate_weather_data(**params)
    features_df = extract_sensor_features(df)

    iso_model = IsolationForest(
        contamination=contamination,
        random_state=params["seed"],
        n_estimators=150,
    )
    iso_model.fit(features_df[ISO_FEATURE_COLUMNS])

    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=params["seed"])
    rf_classifier.fit(features_df[CLF_FEATURE_COLUMNS], df["ground_truth"])

    joblib.dump(iso_model, os.path.join(MODELS_DIR, "isolation_forest.pkl"))
    joblib.dump(rf_classifier, os.path.join(MODELS_DIR, "random_forest.pkl"))
    joblib.dump(
        {"params": params, "contamination": contamination},
        os.path.join(MODELS_DIR, "training_meta.pkl"),
    )

    print(f"Saved isolation_forest.pkl and random_forest.pkl to {os.path.abspath(MODELS_DIR)}")
    return {"params": params, "contamination": contamination}


if __name__ == "__main__":
    train_and_save()
