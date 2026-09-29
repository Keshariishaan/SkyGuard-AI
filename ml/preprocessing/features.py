"""
Feature engineering for the sensor anomaly pipeline.

Ported directly from the original prototype's extract_sensor_features
function. No steps were added, removed, or reordered.
"""

import pandas as pd

# Feature column order the Random Forest classifier expects. Kept as a
# constant here so training and inference always agree on it.
CLF_FEATURE_COLUMNS = [
    "temperature", "humidity", "pressure",
    "temp_diff", "humid_diff", "press_diff",
    "humid_roll_std", "press_deviation",
]

ISO_FEATURE_COLUMNS = ["temperature", "humidity", "pressure"]


def extract_sensor_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract diagnostic features for anomaly detection and fault classification:
    - Raw telemetry values
    - First-order rate of change (diff)
    - Rolling window variance / standard deviation (detects flatline/frozen sensors)
    - Deviation from rolling median (detects drift & localized spikes)
    """
    feats = data[["temperature", "humidity", "pressure"]].copy()

    feats["temp_diff"] = feats["temperature"].diff().fillna(0).abs()
    feats["humid_diff"] = feats["humidity"].diff().fillna(0).abs()
    feats["press_diff"] = feats["pressure"].diff().fillna(0)

    feats["humid_roll_std"] = feats["humidity"].rolling(window=5, min_periods=1).std().fillna(0)
    feats["press_roll_mean"] = feats["pressure"].rolling(window=15, min_periods=1).mean().fillna(feats["pressure"])
    feats["press_deviation"] = feats["pressure"] - feats["press_roll_mean"]

    return feats
