from data_loader import load_market_data
from model_core import run_model
from decision_engine import generate_signal
from regime_adjustment import adjust_for_regime
from trade_filter import apply_trade_filter


def forecast_asset(asset_name, asset_cfg, df_override=None):

    if df_override is not None:
        df = df_override
    else:
        df = load_market_data(asset_cfg["ticker"], asset_cfg)

    model_output = run_model(df)
    regime = adjust_for_regime(df)
    decision = generate_signal(model_output, regime)

    # Filter 1-4 anwenden
    filtered = apply_trade_filter(asset_name, df, decision, asset_cfg)

    latest_close = float(df["close"].iloc[-1])
    prev_close = float(df["close"].iloc[-2])
    daily_return = (latest_close / prev_close) - 1

    prob_up = float(filtered.get("prob_up", decision.get("prob_up", 0.5)))
    prob_down = float(filtered.get("prob_down", 1 - prob_up))

    return {
        "asset": asset_name,
        "signal": filtered.get("final_signal", filtered.get("signal", "HOLD")),
        "confidence": float(filtered.get("confidence", decision.get("confidence", 0.0))),
        "prob_up": round(prob_up, 4),
        "prob_down": round(prob_down, 4),
        "regime": filtered.get("regime", regime),
        "close": round(latest_close, 2),
        "prev_close": round(prev_close, 2),
        "daily_return": round(daily_return * 100, 2),
        "score": round(float(model_output.get("score", 0.0)), 6),
        "rule": filtered.get("rule", ""),
    }
