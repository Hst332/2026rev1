import pandas as pd
from datetime import datetime


REQUIRED_COLUMNS = [
    "asset",
    "prev_close",
    "close",
    "daily_return",
    "signal",
    "confidence",
    "regime",
    "prob_up",
    "rule",
    "timestamp_utc",
]


def validate_forecast_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensures the forecast dataframe always has a stable schema.

    - Adds missing required columns with safe defaults (no crash).
    - Reorders columns into a professional stable output.
    """
    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()

    # if empty, return empty frame with required schema
    if df.empty:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    # Defaults
    now_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    defaults = {
        "asset": "",
        "prev_close": None,
        "close": None,
        "daily_return": None,
        "signal": "HOLD",
        "confidence": 0.0,
        "regime": "neutral",
        "prob_up": 0.5,
        "rule": "",
        "timestamp_utc": now_utc,
    }

    # Add missing columns
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = defaults[col]

    # Ensure types are sane
    # numeric columns
    for col in ["prev_close", "close", "daily_return", "confidence", "prob_up"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # strings
    for col in ["asset", "signal", "regime", "rule", "timestamp_utc"]:
        df[col] = df[col].astype(str)

    # Reorder to stable schema
    df = df[REQUIRED_COLUMNS]

    return df
