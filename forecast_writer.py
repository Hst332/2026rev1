import os
from datetime import datetime
from trade_filter import RULES


def write_index_forecast_txt(df, filename="index_forecast.txt"):
    """
    Writes formatted forecast output + appended validated trading rules.
    """
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = []
    lines.append(f"Index Forecasts – {now}")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Index    | Prev Close | Current | Δ %    | Signal | Conf | Regime | Rule")
    lines.append("-" * 80)

    if df is None or df.empty:
        lines.append("No forecast results (data fetch failed).")
    else:
        for _, r in df.iterrows():
            lines.append(
                f"{r['asset']:<7} | "
                f"{r['prev_close']:>10.2f} | "
                f"{r['close']:>7.2f} | "
                f"{r['daily_return']:>6.2f}% | "
                f"{r['signal']:<5} | "
                f"{r['confidence']:<4.2f} | "
                f"{r['regime']:<7} | "
                f"{r.get('rule','')}"
            )

    lines.append("")
    lines.append("")
    lines.append("TRADING RULES (FINAL – BACKTEST VALIDATED)")
    lines.append("")

    for asset, rule in RULES.items():
        lines.append(asset)
        lines.append(f"- LONG  if prob_up >= {rule['long_entry']:.2f}")
        lines.append(f"- SHORT if prob_up <= {rule['short_entry']:.2f}")
        lines.append("- Otherwise: HOLD")
        lines.append(f"- Note: {rule['note']}")
        lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Saved → {filename}")
