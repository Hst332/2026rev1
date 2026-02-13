from __future__ import annotations

import pandas as pd
from data_loader import load_market_data
from model_core import run_model
from decision_engine import generate_signal
from regime_adjustment import adjust_for_regime


def forecast_asset(asset_name, asset_cfg, df_override=None):

    # Daten laden
    if df_override is not None:
        df = df_override
    else:
        df = load_market_data(asset_cfg["ticker"], asset_cfg)

    # Spalten absichern
    df.columns = [c.lower() for c in df.columns]

    if "close" not in df.columns:
        raise KeyError("close column missing")

    # Modell
    model_output = run_model(df)
    regime = adjust_for_regime(df)
    decision = generate_signal(model_output, regime)

    latest_close = float(df["close"].iloc[-1])
    prev_close = float(df["close"].iloc[-2])
    daily_return = (latest_close / prev_close) - 1

    prob_up = float(decision.get("prob_up", 0.5))
    prob_down = 1.0 - prob_up

    # === Data Freshness ===
    latest_ts = df.index[-1]

    if isinstance(latest_ts, pd.Timestamp):
        if latest_ts.tzinfo is not None:
            latest_ts = latest_ts.tz_convert("UTC").tz_localize(None)

    now_utc = pd.Timestamp.utcnow().tz_localize(None)
    data_age_minutes = (now_utc - pd.Timestamp(latest_ts)).total_seconds() / 60.0

    return {
        "asset": asset_name,
        "signal": decision["signal"],
        "confidence": float(decision["confidence"]),
        "prob_up": round(prob_up, 4),
        "prob_down": round(prob_down, 4),
        "regime": regime,
        "close": round(latest_close, 2),
        "prev_close": round(prev_close, 2),
        "daily_return": round(daily_return * 100, 2),
        "score": round(float(model_output.get("score", 0.0)), 4),
        "data_timestamp": str(latest_ts),
        "data_age_min": round(float(data_age_minutes), 1),
    }
