from optimizer import run_optimizer

indices = {
    "DAX": "backtests/DAX_backtest.csv",
    "ATX": "backtests/ATX_backtest.csv",
    "NASDAQ": "backtests/NASDAQ_backtest.csv",
    "SP500": "backtests/SP500_backtest.csv",
    "DOW": "backtests/DOW_backtest.csv",
    "NIKKEI": "backtests/NIKKEI_backtest.csv",
}

for name, path in indices.items():
    print(f"Optimizing {name}...")

    cfg, stats = run_optimizer(path)

    print("BEST CONFIG:")
    print(cfg)
    print("RESULT:")
    print(stats)
    print("--------------")
