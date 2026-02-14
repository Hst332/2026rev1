from data_loader import load_market_data
from model_core import run_model
from decision_engine import generate_signal
from regime_adjustment import adjust_for_regime


def forecast_asset(asset_name, asset_cfg, df_override=None):
    # Backtest Slice oder Live Daten
    if df_override is not None:
        df = df_override
    else:
        df = load_market_data(asset_cfg["ticker"], asset_cfg)

    model_output = run_model(df)
    regime = adjust_for_regime(df)
    decision = generate_signal(model_output, regime)

    # Pflicht: close muss existieren (data_loader normalisiert)
    latest_close = float(df["close"].iloc[-1])
    prev_close = float(df["close"].iloc[-2])
    daily_return = (latest_close / prev_close) - 1.0

    prob_up = float(decision.get("prob_up", 0.5))
    prob_down = 1.0 - prob_up
    confidence = float(decision.get("confidence", abs(prob_up - 0.5) * 2.0))

    return {
        "asset": asset_name,
        "signal": decision.get("signal", "HOLD"),
        "confidence": round(confidence, 4),
        "prob_up": round(prob_up, 4),
        "prob_down": round(prob_down, 4),
        "regime": regime,
        "close": round(latest_close, 2),
        "prev_close": round(prev_close, 2),
        "daily_return": round(daily_return * 100.0, 2),  # Prozent
        "score": round(float(model_output.get("score", 0.0)), 6),
    }
