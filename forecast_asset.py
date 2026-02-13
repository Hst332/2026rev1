latest_timestamp = df.index[-1]

# Falls timezone-aware → in UTC umwandeln
if hasattr(latest_timestamp, "tzinfo") and latest_timestamp.tzinfo is not None:
    latest_timestamp = latest_timestamp.tz_convert("UTC").tz_localize(None)

data_age_minutes = (
    pd.Timestamp.utcnow().tz_localize(None) - latest_timestamp
).total_seconds() / 60

return {
    "asset": asset_name,
    "signal": decision["signal"],
    "confidence": decision["confidence"],
    "prob_up": prob_up,
    "prob_down": prob_down,
    "regime": regime,
    "close": round(float(latest_close), 2),
    "prev_close": round(float(prev_close), 2),
    "daily_return": round(daily_return * 100, 2),
    "score": round(model_output.get("score", 0.0), 4),
    "data_timestamp": str(latest_timestamp),
    "data_age_min": round(data_age_minutes, 1),
}
