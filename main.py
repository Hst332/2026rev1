from datetime import datetime
import os
import pandas as pd

from config import ASSETS
from forecast_asset import forecast_asset
from trade_filter import apply_trade_filter
from forecast_writer import write_index_forecast_txt

os.makedirs("forecasts", exist_ok=True)

results = []

timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

for asset_name, cfg in ASSETS.items():

    print(f"Running forecast for {asset_name}")

    try:
        forecast = forecast_asset(asset_name, cfg)

        signal_final, rule_long, rule_short, rule_label = apply_trade_filter(
            asset_name,
            forecast["prob_up"]
        )

        row = {
            "timestamp_utc": timestamp,
            "asset": asset_name,
            "ticker": cfg["ticker"],
            "price_current": forecast["close"],
            "price_prev_close": forecast["prev_close"],
            "return_daily_pct": forecast["daily_return"],
            "score": forecast["score"],
            "prob_up": forecast["prob_up"],
            "prob_down": forecast["prob_down"],
            "confidence": forecast["confidence"],
            "regime": forecast["regime"],
            "rule_long_min": rule_long,
            "rule_short_max": rule_short,
            "signal_raw": forecast["signal"],
            "signal_final": signal_final,
            "rule_label": rule_label,
            "data_status": "ok",
        }

        results.append(row)

    except Exception as e:

        print(f"ERROR {asset_name}: {e}")

        results.append({
            "timestamp_utc": timestamp,
            "asset": asset_name,
            "ticker": cfg["ticker"],
            "price_current": 0,
            "price_prev_close": 0,
            "return_daily_pct": 0,
            "score": 0,
            "prob_up": 0.5,
            "prob_down": 0.5,
            "confidence": 0,
            "regime": "error",
            "rule_long_min": 0,
            "rule_short_max": 0,
            "signal_raw": "HOLD",
            "signal_final": "HOLD",
            "rule_label": "error",
            "data_status": str(e),
        })

df = pd.DataFrame(results)

df = validate_forecast_dataframe(df)

csv_path = "forecasts/daily_index_forecast.csv"
df.to_csv(csv_path, index=False)

write_index_forecast_txt(df)

print("Forecast completed successfully.")
