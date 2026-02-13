import pandas as pd
from data_loader import load_market_data
from model_core import run_model
from decision_engine import generate_signal

def run_backtest(symbol):
    df = load_market_data(symbol)

    results = []
    for i in range(10, len(df)):
        window = df.iloc[:i]
        model_output = run_model(window)
        regime = "neutral"
        signal = generate_signal(model_output, regime)

        results.append({
            "date": window.index[-1],
            "signal": signal["signal"],
            "confidence": signal["confidence"]
        })

    return pd.DataFrame(results)

if __name__ == "__main__":
    bt = run_backtest("^GDAXI")
    print(bt.tail())
