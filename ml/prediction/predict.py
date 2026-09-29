"""
Prediction layer. Loads the persisted models when the request matches
the trained default configuration; otherwise fits both models live on
the requested configuration - identical to what the original Streamlit
prototype did on every rerun. No algorithm, feature, or parameter was
changed from the original app.py.
"""

import os

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier

from ml.preprocessing.features import CLF_FEATURE_COLUMNS, ISO_FEATURE_COLUMNS
from ml.training.train import DEFAULT_CONTAMINATION, DEFAULT_PARAMS, MODELS_DIR

_ISO_PATH = os.path.join(MODELS_DIR, "isolation_forest.pkl")
_RF_PATH = os.path.join(MODELS_DIR, "random_forest.pkl")

_cache = {}  # in-process cache keyed by (seed, contamination) -> (iso_model, rf_model)


def _matches_default(params: dict, contamination: float) -> bool:
    return params == DEFAULT_PARAMS and contamination == DEFAULT_CONTAMINATION


def _load_persisted_models():
    if os.path.exists(_ISO_PATH) and os.path.exists(_RF_PATH):
        return joblib.load(_ISO_PATH), joblib.load(_RF_PATH)
    return None, None


def run_prediction(df: pd.DataFrame, features_df: pd.DataFrame, params: dict, contamination: float) -> pd.DataFrame:
    """
    Runs the exact two-stage pipeline from the original prototype:
      A. IsolationForest flags anomalies (-1 anomaly, 1 normal)
      B. RandomForestClassifier labels the fault type for every row
      C. final_diagnosis = predicted fault type where anomalous, else "Normal"

    Returns df with iso_forest_pred, is_anomaly, anomaly_score,
    predicted_fault and final_diagnosis columns added, unchanged from
    the original prototype's output schema.
    """
    seed = params["seed"]
    cache_key = (seed, contamination, params["rows"])

    iso_model = rf_classifier = None

    if _matches_default(params, contamination):
        iso_model, rf_classifier = _load_persisted_models()

    if iso_model is None or rf_classifier is None:
        if cache_key in _cache:
            iso_model, rf_classifier = _cache[cache_key]
        else:
            # Fit fresh, exactly as app.py does on every Streamlit rerun:
            # the contamination slider and the fault-injection sliders change
            # the dataset and the correct ground truth, so both models must
            # be refit on this specific configuration.
            iso_model = IsolationForest(
                contamination=contamination,
                random_state=seed,
                n_estimators=150,
            )
            iso_model.fit(features_df[ISO_FEATURE_COLUMNS])

            rf_classifier = RandomForestClassifier(n_estimators=100, random_state=seed)
            rf_classifier.fit(features_df[CLF_FEATURE_COLUMNS], df["ground_truth"])

            _cache[cache_key] = (iso_model, rf_classifier)

    df = df.copy()
    df["iso_forest_pred"] = iso_model.predict(features_df[ISO_FEATURE_COLUMNS])
    df["is_anomaly"] = df["iso_forest_pred"] == -1
    df["anomaly_score"] = iso_model.decision_function(features_df[ISO_FEATURE_COLUMNS])

    df["predicted_fault"] = rf_classifier.predict(features_df[CLF_FEATURE_COLUMNS])
    df["final_diagnosis"] = np.where(df["is_anomaly"], df["predicted_fault"], "Normal")

    return df
