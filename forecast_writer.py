from __future__ import annotations

from datetime import datetime
from trade_filter import RULES


def write_index_forecast_txt(df, filename="index_forecast.txt"):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = []
    lines.append(f"Index Forecasts – {now}")
    lines.append("=" * 110)
    lines.append("")
    lines.append("Index    | Prev Close | Current | Δ %    | Signal | Conf | Regime   | ProbUp | Rule")
    lines.append("-" * 110)

    if df is None or df.empty:
        lines.append("No forecast results (data fetch failed).")
    else:
        for _, r in df.iterrows():
            lines.append(
                f"{str(r['asset']):<8} | "
                f"{float(r['prev_close']):>10.2f} | "
                f"{float(r['close']):>7.2f} | "
                f"{float(r['daily_return']):>6.2f}% | "
                f"{str(r['signal']):<6} | "
                f"{float(r['confidence']):>4.2f} | "
                f"{str(r['regime']):<8} | "
                f"{float(r['prob_up']):>5.2f} | "
                f"{str(r['rule'])}"
            )

    lines.append("")
    lines.append("")
    lines.append("TRADING RULES (Thresholds)")
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
