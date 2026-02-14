from forecast_asset import forecast_asset
from config import ASSETS
import pandas as pd
from datetime import datetime
import os

from forecast_writer import write_index_forecast_txt
from schema_validator import validate_forecast_dataframe

os.makedirs("forecasts", exist_ok=True)


def main():
    all_results = []
    run_ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    for asset, cfg in ASSETS.items():
        print(f"Running forecast for {asset}")
        try:
            result = forecast_asset(asset, cfg)

            # Pflichtfelder IMMER setzen (damit Schema Validator nie mehr bricht)
            result.setdefault("asset", asset)
            result.setdefault("timestamp_utc", run_ts)
            result.setdefault("rule", result.get("rule", ""))  # falls forecast_asset es liefert
            all_results.append(result)

        except Exception as e:
            print(f"ERROR {asset}: {e}")

    df = pd.DataFrame(all_results)

    # Falls keine Daten: trotzdem mit fixen Spalten speichern & txt schreiben
    df = validate_forecast_dataframe(df)

    filename = "forecasts/daily_index_forecast.csv"
    df.to_csv(filename, index=False)
    print("Saved:", filename)

    write_index_forecast_txt(df)


if __name__ == "__main__":
    main()
