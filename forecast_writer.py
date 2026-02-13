from datetime import datetime, timezone
from pathlib import Path
from trade_filter import RULES

def write_forecasts(forecasts, out_dir="forecasts"):
    Path(out_dir).mkdir(exist_ok=True)

    # CSV
    csv_path = Path(out_dir) / "daily_index_forecast.csv"
    import pandas as pd
    pd.DataFrame(forecasts).to_csv(csv_path, index=False)

    # TXT
    txt_file = "index_forecast.txt"
    runtime = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    with open(txt_file, "w") as f:
        f.write(f"Index Forecasts – {runtime}\n")
        f.write("=" * 80 + "\n\n")
        f.write("Index    | Prev Close | Current | Δ %    | Signal | Conf | Regime | Rule\n")
        f.write("-" * 80 + "\n")

        for item in forecasts:
            rule_note = item.get("rule_note", "")
            f.write(
                f"{item['asset']:<8} | {item['prev_close']:>10.2f} | {item['close']:>7.2f} | "
                f"{item['daily_return']:>6.2f}% | {item['signal']:<6} | {item['confidence']:<4.2f} | "
                f"{item['regime']:<7} | {rule_note}\n"
            )

        f.write("\n\nTRADING RULES (FINAL – BACKTEST VALIDATED)\n\n")
        for asset, rule in RULES.items():
            f.write(f"{asset}\n")
            f.write(f"- LONG  if prob_up >= {rule['long_entry']:.2f}\n")
            f.write(f"- SHORT if prob_up <= {rule['short_entry']:.2f}\n")
            f.write(f"- Otherwise: HOLD\n")
            f.write(f"- Note: {rule.get('note','')}\n\n")

    return str(csv_path), txt_file
