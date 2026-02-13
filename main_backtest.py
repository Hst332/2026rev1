from asset_config import ASSETS
from backtest_engine import run_backtest
from backtest_writer import save_backtest_csv


all_results = {}

for asset, cfg in ASSETS.items():

    results = run_backtest(asset, cfg)

    filename = f"backtest_{asset}.csv"
    save_backtest_csv(results, filename)

    all_results[asset] = results

print("BACKTEST FINISHED")
