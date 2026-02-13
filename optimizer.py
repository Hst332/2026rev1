import pandas as pd
import itertools

def apply_filters(df, cfg):
    data = df.copy()

    # Confidence Filter
    if cfg["min_conf"] is not None:
        data = data[data["confidence"] >= cfg["min_conf"]]

    # Trendfilter
    if cfg["trend_filter"]:
        data = data[
            ((data["close"] > data["ema200"]) & (data["signal"] == "BUY")) |
            ((data["close"] < data["ema200"]) & (data["signal"] == "SELL"))
        ]

    # ATR Filter
    if cfg["atr_filter"]:
        data = data[data["atr"] > data["atr_median"]]

    # BUY / SELL Auswahl
    if cfg["side"] == "BUY":
        data = data[data["signal"] == "BUY"]
    elif cfg["side"] == "SELL":
        data = data[data["signal"] == "SELL"]

    # Wochentage
    if cfg["weekday"] is not None:
        data = data[data["weekday"].isin(cfg["weekday"])]

    return data


def evaluate_strategy(df):
    if len(df) < 100:
        return None

    winrate = (df["future_return"] > 0).mean()
    avg_return = df["future_return"].mean()

    gains = df[df["future_return"] > 0]["future_return"].sum()
    losses = abs(df[df["future_return"] < 0]["future_return"].sum())
    profit_factor = gains / losses if losses > 0 else 0

    return {
        "trades": len(df),
        "winrate": winrate,
        "avg_return": avg_return,
        "profit_factor": profit_factor,
    }


def run_optimizer(csv_path):

    df = pd.read_csv(csv_path)

    conf_levels = [0.55, 0.60, 0.65, 0.70, 0.75]
    trend_options = [True, False]
    atr_options = [True, False]
    sides = ["both", "BUY", "SELL"]
    weekday_options = [None, [1,2,3], [2,3,4]]

    best_result = None
    best_cfg = None

    for cfg in itertools.product(conf_levels, trend_options, atr_options, sides, weekday_options):

        config = {
            "min_conf": cfg[0],
            "trend_filter": cfg[1],
            "atr_filter": cfg[2],
            "side": cfg[3],
            "weekday": cfg[4]
        }

        filtered = apply_filters(df, config)
        stats = evaluate_strategy(filtered)

        if stats is None:
            continue

        if best_result is None or stats["winrate"] > best_result["winrate"]:
            best_result = stats
            best_cfg = config

    return best_cfg, best_result
