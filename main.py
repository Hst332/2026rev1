from __future__ import annotations

import os
from datetime import datetime

import pandas as pd

from forecast_asset import forecast_asset
from config import ASSETS
from forecast_writer import write_index_forecast_txt
from schema_validator import validate_forecast_dataframe


def main():
    os.makedirs("forecasts", exist_ok=True)

    results = []
    for asset, cfg in ASSETS.items():
        print(f"Running forecast for {asset}")
        try:
            r = forecast_asset(asset, cfg)
            results.append(r)
        except Exception as e:
            print(f"ERROR {asset}: {e}")

    df = pd.DataFrame(results)

    # Validator: gibt df zurück (safe auch wenn df leer ist)
    df = validate_forecast_dataframe(df) if not df.empty else df

    # CSV immer schreiben (auch wenn leer, dann nur header)
    out_csv = "forecasts/daily_index_forecast.csv"
    df.to_csv(out_csv, index=False)
    print("Saved:", out_csv)

    # TXT schreiben
    write_index_forecast_txt(df)


if __name__ == "__main__":
    main()
