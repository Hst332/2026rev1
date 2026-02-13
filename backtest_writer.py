import pandas as pd

def save_backtest_csv(results, filename):
    rows = []

    for r in results:
        future_return = r.get("future_return", r.get("return"))

        rows.append({
            "date": r.get("date"),
            "symbol": r.get("symbol"),
            "signal": r.get("signal"),
            "close": r.get("close"),
            "future_close": r.get("future_close"),
            "future_return": future_return,
            "confidence": r.get("confidence"),
            "prob_up": r.get("prob_up"),
            "prob_down": r.get("prob_down"),
            "regime": r.get("regime"),
        })

    pd.DataFrame(rows).to_csv(filename, index=False)
    print("CSV WRITTEN:", filename)
