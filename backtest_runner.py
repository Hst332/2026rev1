from data_loader import load_market_data
from forecast_asset import forecast_asset
from backtest_engine import run_backtest as backtest_engine

def run_backtest(asset, cfg, lookback=252):
    df = load_market_data(asset, cfg)

    results = []

    for i in range(lookback, len(df)):
        sliced_df = df.iloc[:i].copy()

        forecast = forecast_asset(asset, cfg, df_override=sliced_df)

        forecast["date"] = sliced_df.index[-1]
        forecast["future_return"] = (
            df["close"].iloc[i] / df["close"].iloc[i - 1] - 1
        ) * 100

        results.append(forecast)
from backtest_writer import save_backtest_csv

def run_backtest(asset_name, asset_cfg):
    results = backtest_engine(asset_name, asset_cfg)

    # CSV direkt nach Berechnung der Trades speichern
    save_backtest_csv(results, filename=f"raw_backtest_{asset_name}.csv")

    return results


    return results
