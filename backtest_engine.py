from forecast_asset import forecast_asset
from data_loader import load_market_data


def run_backtest(asset_name, asset_cfg):

    print(f"Running backtest for {asset_name}")

    df = load_market_data(asset_cfg["ticker"], asset_cfg)

    results = []

    for i in range(200, len(df) - 5):

        sliced_df = df.iloc[:i].copy()

        forecast = forecast_asset(asset_name, asset_cfg, df_override=sliced_df)

        close_now = df["close"].iloc[i]
        future_close = df["close"].iloc[i + 5]

        future_return = (future_close / close_now) - 1

        results.append({
            "date": df.index[i],
            "signal": forecast["signal"],
            "confidence": forecast["confidence"],
            "prob_up": forecast["prob_up"],
            "prob_down": forecast["prob_down"],
            "regime": forecast["regime"],
            "future_return": future_return
        })

    return results
