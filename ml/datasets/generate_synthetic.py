"""
Synthetic weather telemetry generator with fault injection.

Ported directly from the original SkyGuard AI Streamlit prototype
(app.py -> generate_weather_data). Logic and formulas are unchanged;
only the caching decorator (@st.cache_data) was removed since this
module no longer runs inside Streamlit.
"""

from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def generate_weather_data(
    rows: int,
    seed: int,
    spike_en: bool,
    spike_t: float,
    spike_idx: int,
    frozen_en: bool,
    frozen_dur: int,
    frozen_idx: int,
    drift_en: bool,
    drift_dur: int,
    drift_idx: int,
) -> pd.DataFrame:
    """
    Generate synthetic hourly weather telemetry (Temperature, Humidity, Pressure)
    and inject intentional hardware sensor anomalies. Identical algorithm to the
    original prototype's generate_weather_data function.
    """
    np.random.seed(seed)
    start_time = datetime(2025, 1, 1, 0, 0, 0)
    timestamps = [start_time + timedelta(hours=i) for i in range(rows)]
    hours = np.arange(rows)

    # 1. Baseline diurnal patterns
    temp_diurnal = 21.0 + 7.0 * np.sin(2 * np.pi * (hours - 8) / 24)
    temp_noise = np.random.normal(0, 0.8, size=rows)
    temperature = temp_diurnal + temp_noise

    humid_diurnal = 62.0 - 20.0 * np.sin(2 * np.pi * (hours - 8) / 24)
    humid_noise = np.random.normal(0, 1.5, size=rows)
    humidity = np.clip(humid_diurnal + humid_noise, 20.0, 99.0)

    press_wave = 1013.25 + 5.0 * np.sin(2 * np.pi * hours / 72)
    press_noise = np.random.normal(0, 0.4, size=rows)
    pressure = press_wave + press_noise

    ground_truth = ["Normal"] * rows

    # 2. Fault 1: Temperature Spike
    if spike_en and 0 <= spike_idx < rows:
        temperature[spike_idx] = spike_t
        ground_truth[spike_idx] = "Spike"

    # 3. Fault 2: Frozen Humidity
    if frozen_en and 0 <= frozen_idx < rows - frozen_dur:
        frozen_val = round(float(humidity[frozen_idx]), 2)
        for i in range(frozen_idx, frozen_idx + frozen_dur):
            humidity[i] = frozen_val
            ground_truth[i] = "Frozen"

    # 4. Fault 3: Pressure Drift
    if drift_en and 0 <= drift_idx < rows - drift_dur:
        drift_delta = np.linspace(0.5, 25.0, drift_dur)
        for step, i in enumerate(range(drift_idx, drift_idx + drift_dur)):
            pressure[i] += drift_delta[step]
            ground_truth[i] = "Drift"

    df = pd.DataFrame({
        "timestamp": timestamps,
        "hour_index": hours,
        "temperature": np.round(temperature, 2),
        "humidity": np.round(humidity, 2),
        "pressure": np.round(pressure, 2),
        "ground_truth": ground_truth,
    })
    return df
