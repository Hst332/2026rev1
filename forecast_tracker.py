from __future__ import annotations

import os
from datetime import datetime, timedelta
import pandas as pd


HISTORY_PATH = "forecasts/history.csv"
VALIDATION_PATH = "forecasts/validation.csv"


def _ensure_forecasts_dir():
    os.makedirs("forecasts", exist_ok=True)


def append_history(df_today: pd.DataFrame, run_ts_utc: str) -> None:
    """
    Append today's forecasts to forecasts/history.csv
    Expected columns at least:
      asset, prev_close, current, daily_return, signal, confidence, regime, prob_up, score, rule
    """
    _ensure_forecasts_dir()

    df = df_today.copy()
    df["timestamp_utc"] = run_ts_utc

    # keep stable column order (missing columns are allowed)
    preferred = [
        "timestamp_utc",
        "asset",
        "prev_close",
        "current",
        "daily_return",
        "signal",
        "confidence",
        "regime",
        "prob_up",
        "score",
        "rule",
    ]
    cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
    df = df[cols]

    if os.path.exists(HISTORY_PATH):
        old = pd.read_csv(HISTORY_PATH)
        out = pd.concat([old, df], ignore_index=True)
    else:
        out = df

    out.to_csv(HISTORY_PATH, index=False)


def validate_yesterday(df_today: pd.DataFrame, run_ts_utc: str) -> pd.DataFrame:
    """
    Compare yesterday's prediction with today's realized move.
    realized_return_1d is based on today's close vs prev_close (already in df_today as daily_return).
    Then match with yesterday's stored forecast signal for same asset.
    """
    _ensure_forecasts_dir()

    if not os.path.exists(HISTORY_PATH):
        # nothing to validate yet
        empty = pd.DataFrame(columns=[
            "date_utc",
            "asset",
            "yesterday_signal",
            "yesterday_prob_up",
            "yesterday_confidence",
            "today_return_pct",
            "hit_1d",
        ])
        empty.to_csv(VALIDATION_PATH, index=False)
        return empty

    hist = pd.read_csv(HISTORY_PATH)

    # define "yesterday" by date (UTC)
    run_dt = datetime.strptime(run_ts_utc, "%Y-%m-%d %H:%M UTC")
    yday_date = (run_dt.date() - timedelta(days=1)).isoformat()

    # take the latest entry per asset from that UTC date
    hist["date_utc"] = pd.to_datetime(hist["timestamp_utc"].str.replace(" UTC", ""), errors="coerce").dt.date.astype(str)
    yday = hist[hist["date_utc"] == yday_date].copy()
    if yday.empty:
        # no yday record (first run or weekend gap)
        empty = pd.DataFrame(columns=[
            "date_utc",
            "asset",
            "yesterday_signal",
            "yesterday_prob_up",
            "yesterday_confidence",
            "today_return_pct",
            "hit_1d",
        ])
        empty.to_csv(VALIDATION_PATH, index=False)
        return empty

    yday = yday.sort_values("timestamp_utc").groupby("asset", as_index=False).tail(1)

    today = df_today.copy()
    today["today_return_pct"] = today["daily_return"]

    merged = yday.merge(today[["asset", "today_return_pct"]], on="asset", how="inner")

    def hit(sig: str, ret: float) -> int:
        if pd.isna(ret):
            return 0
        if sig == "BUY":
            return int(ret > 0)
        if sig == "SELL":
            return int(ret < 0)
        # HOLD: treat as "no bet" -> 0 (or you can use 1 if abs(ret) small)
        return 0

    merged["hit_1d"] = merged.apply(lambda r: hit(str(r.get("signal", "")), float(r.get("today_return_pct", 0.0))), axis=1)

    out = pd.DataFrame({
        "date_utc": yday_date,
        "asset": merged["asset"],
        "yesterday_signal": merged["signal"],
        "yesterday_prob_up": merged.get("prob_up", pd.Series([None]*len(merged))),
        "yesterday_confidence": merged.get("confidence", pd.Series([None]*len(merged))),
        "today_return_pct": merged["today_return_pct"],
        "hit_1d": merged["hit_1d"],
    })

    out.to_csv(VALIDATION_PATH, index=False)
    return out
