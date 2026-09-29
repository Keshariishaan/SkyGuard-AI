"""
The ONE function the backend is allowed to call. Nothing outside ml/
should import generate_synthetic, features, or predict directly - this
keeps the "Frontend -> Backend -> ML -> Database" boundary real.
"""

import pandas as pd

from ml.datasets.generate_synthetic import generate_weather_data
from ml.preprocessing.features import extract_sensor_features
from ml.prediction.predict import run_prediction


def run_pipeline(
    rows: int,
    seed: int,
    spike_en: bool, spike_t: float, spike_idx: int,
    frozen_en: bool, frozen_dur: int, frozen_idx: int,
    drift_en: bool, drift_dur: int, drift_idx: int,
    contamination: float,
) -> pd.DataFrame:
    """
    Full pipeline: generate synthetic telemetry -> engineer features ->
    IsolationForest anomaly detection -> RandomForest fault classification.
    Returns one row per hour with the same columns the original
    prototype produced.
    """
    params = dict(
        rows=rows, seed=seed,
        spike_en=spike_en, spike_t=spike_t, spike_idx=spike_idx,
        frozen_en=frozen_en, frozen_dur=frozen_dur, frozen_idx=frozen_idx,
        drift_en=drift_en, drift_dur=drift_dur, drift_idx=drift_idx,
    )

    df = generate_weather_data(**params)
    features_df = extract_sensor_features(df)
    result = run_prediction(df, features_df, params, contamination)
    return result
