from forecast_asset import forecast_asset

def run_live_forecasts(assets):
    results = []
    for asset, cfg in assets.items():
        try:
            r = forecast_asset(asset, cfg)
            results.append(r)
        except Exception as e:
            print(f"ERROR {asset}: {e}")
    return results
