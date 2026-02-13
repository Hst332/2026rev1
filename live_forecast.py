from forecast_asset import forecast_asset

ASSETS = {
    "DAX": {"ticker": "^GDAXI"},
    "ATX": {"ticker": "^ATX"},
    "DOW": {"ticker": "^DJI"},
    "NASDAQ": {"ticker": "^IXIC"},
    "SP500": {"ticker": "^GSPC"},
    "NIKKEI": {"ticker": "^N225"},
}


def run_live_forecast():
    results = []

    print("\n==============================")
    print(" LIVE FORECAST ENGINE STARTED ")
    print("==============================\n")

    for asset, cfg in ASSETS.items():
        try:
            print(f"Running live forecast for {asset}")

            forecast = forecast_asset(asset, cfg)

            results.append(forecast)

            print(
                f"{asset} | "
                f"Signal: {forecast.get('signal')} | "
                f"Close: {forecast.get('close')} | "
                f"Confidence: {forecast.get('confidence')} | "
                f"Regime: {forecast.get('regime')}"
            )

        except Exception as e:
            print(f"ERROR in {asset}: {e}")

    return results


def save_live_csv(results):
    import pandas as pd
    from datetime import datetime

    if not results:
        print("No live results to save.")
        return

    df = pd.DataFrame(results)

    filename = f"live_forecast_{datetime.utcnow().strftime('%Y-%m-%d')}.csv"
    df.to_csv(filename, index=False)

    print(f"\nLive forecast saved: {filename}")


if __name__ == "__main__":
    live_results = run_live_forecast()
    save_live_csv(live_results)
