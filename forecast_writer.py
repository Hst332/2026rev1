from datetime import datetime


def write_index_forecast_txt(df, filename="index_forecast.txt"):

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    lines = []
    lines.append(f"Index Forecasts – {now}")
    lines.append("=" * 110)
    lines.append("")
    lines.append(
        "Index    | Prev Close | Current | Δ %    | Conf | Regime   | ProbUp | Signal"
    )
    lines.append(
        "-" * 110
    )

    if df.empty:
        lines.append("No forecast results (data fetch failed).")
    else:
        for _, row in df.iterrows():
            lines.append(
                f"{row['asset']:<8} | "
                f"{row['prev_close']:>10.2f} | "
                f"{row['close']:>7.2f} | "
                f"{row['daily_return']:>6.2f}% | "
                f"{row['confidence']:>4.2f} | "
                f"{row['regime']:<8} | "
                f"{row['prob_up']:>6.2f} | "
                f"{row['signal']:<5}"
            )

    lines.append("")
    lines.append("")
    lines.append("TRADING RULES")
    lines.append("-" * 20)
    lines.append("DAX     LONG >= 0.56 | SHORT <= 0.44")
    lines.append("ATX     LONG >= 0.58 | SHORT <= 0.42")
    lines.append("DOW     LONG >= 0.55 | SHORT <= 0.45")
    lines.append("NASDAQ  LONG >= 0.60 | SHORT <= 0.40")
    lines.append("SP500   LONG >= 0.56 | SHORT <= 0.44")
    lines.append("NIKKEI  LONG >= 0.59 | SHORT <= 0.41")

    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"Saved: {filename}")
