from __future__ import annotations
from typing import Dict, Any, Tuple
import pandas as pd


# =========================
# Parameter pro Index
# =========================
# ==============================================================
# MEASURE 1-4: Trade Filter (no "Maßnahme 5")
# --------------------------------------------------------------
# Ziel: Ohne großes Refactoring die Trefferquote erhöhen,
# indem wir nur dann traden, wenn die Modell-Wahrscheinlichkeit
# klar genug ist (Neutralzone = HOLD).
# ==============================================================

FILTER_PARAMS = {
    "DAX": {
        "long_th": 0.56, "short_th": 0.44,
        "ma_len": 200,
        "atr_pct_max": 2.2,
        "cooldown_absret_max": 2.5,
    },
    "ATX": {
        "long_th": 0.58, "short_th": 0.42,
        "ma_len": 200,
        "atr_pct_max": 2.0,
        "cooldown_absret_max": 2.0,
    },
    "DOW": {
        "long_th": 0.55, "short_th": 0.45,
        "ma_len": 150,
        "atr_pct_max": 1.6,
        "cooldown_absret_max": 2.0,
    },
    "NASDAQ": {
        "long_th": 0.60, "short_th": 0.40,
        "ma_len": 200,
        "atr_pct_max": 2.8,
        "cooldown_absret_max": 3.0,
    },
    "SP500": {
        "long_th": 0.56, "short_th": 0.44,
        "ma_len": 200,
        "atr_pct_max": 1.8,
        "cooldown_absret_max": 2.0,
    },
    "NIKKEI": {
        "long_th": 0.59, "short_th": 0.41,
        "ma_len": 200,
        "atr_pct_max": 2.6,
        "cooldown_absret_max": 3.0,
    },
}

# Backwards-compatible alias used by forecast_writer.py
# (RULES enthält die finalen Entry-Thresholds und optionale Notizen)
RULES = {
    asset: {
        "long": float(params["long_th"]),
        "short": float(params["short_th"]),
        "note": "",
    }
    for asset, params in FILTER_PARAMS.items()
}

# Optional: Notizen (nur Text, beeinflusst die Logik nicht)
RULES["DAX"]["note"] = "Trendfolge, keine Trades in Neutralzone"
RULES["ATX"]["note"] = "Stärkerer Filter, weniger Trades"
RULES["DOW"]["note"] = "Stabil, engeres Band ok"
RULES["NASDAQ"]["note"] = "Volatil → höhere Schwelle"
RULES["SP500"]["note"] = "Mittlere Schwelle, breit diversifiziert"
RULES["NIKKEI"]["note"] = "Trendstark, aber Gap-Risiko"


# =========================
# Helper
# =========================
def _get_series(df: pd.DataFrame, name: str) -> pd.Series:
    if name not in df.columns:
        raise KeyError(f"Missing column '{name}'. Have: {list(df.columns)}")
    return df[name].astype(float)


def _compute_ma(close: pd.Series, n: int) -> float:
    if len(close) < n:
        # Falls Dataset kürzer ist (sollte bei 1y daily nicht passieren)
        n = max(20, min(n, len(close)))
    return float(close.rolling(n).mean().iloc[-1])


def _compute_atr_pct(df: pd.DataFrame, n: int = 14) -> float:
    """
    ATR% ~ Average True Range / Close * 100
    True Range nutzt high/low/close.
    """
    high = _get_series(df, "high")
    low = _get_series(df, "low")
    close = _get_series(df, "close")

    prev_close = close.shift(1)

    tr1 = (high - low).abs()
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(n).mean()
    atr_last = float(atr.iloc[-1])
    close_last = float(close.iloc[-1])

    if close_last == 0:
        return 999.0
    return (atr_last / close_last) * 100.0


def _yesterday_abs_return_pct(close: pd.Series) -> float:
    if len(close) < 2:
        return 0.0
    r = (float(close.iloc[-1]) / float(close.iloc[-2]) - 1.0) * 100.0
    return abs(r)


# =========================
# Hauptfunktion: Filter
# =========================
def apply_trade_filter(
    asset_name: str,
    df: pd.DataFrame,
    decision: Dict[str, Any],
    asset_cfg: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Nimmt model decision (prob_up, signal etc.) und macht FINAL signal + rule string.

    Erwartet df-Spalten: close, high, low (open optional).
    """
    params = FILTER_PARAMS.get(asset_name)
    if params is None:
        # Fallback: keine Regeln definiert -> Entscheidung so lassen
        return {**decision, "final_signal": decision.get("signal", "HOLD"), "rule": "no_params"}

    prob_up = float(decision.get("prob_up", 0.5))
    prob_down = 1.0 - prob_up

    close = _get_series(df, "close")

    # ---- Maßnahme 1: Neutralzone / Schwellen
    if prob_up >= params["long_th"]:
        base = "BUY"
        rule = f"M1:prob_up>={params['long_th']}"
    elif prob_up <= params["short_th"]:
        base = "SELL"
        rule = f"M1:prob_up<={params['short_th']}"
    else:
        return {**decision, "final_signal": "HOLD", "rule": "M1:neutral_zone"}

    # ---- Maßnahme 2: Trendfilter (MA)
    ma = _compute_ma(close, params["ma_len"])
    last_close = float(close.iloc[-1])

    if base == "BUY" and not (last_close > ma):
        return {**decision, "final_signal": "HOLD", "rule": f"{rule}+M2:block_trend(close<=MA{params['ma_len']})"}
    if base == "SELL" and not (last_close < ma):
        return {**decision, "final_signal": "HOLD", "rule": f"{rule}+M2:block_trend(close>=MA{params['ma_len']})"}

    rule = f"{rule}+M2:trend_ok"

    # ---- Maßnahme 3: Volatilitätsfilter (ATR%)
    atr_pct = _compute_atr_pct(df, n=14)
    if atr_pct > params["atr_pct_max"]:
        return {**decision, "final_signal": "HOLD", "rule": f"{rule}+M3:block_ATR({atr_pct:.2f}%>{params['atr_pct_max']}%)"}
    rule = f"{rule}+M3:atr_ok({atr_pct:.2f}%)"

    # ---- Maßnahme 4: Cooldown nach Extremtag
    y_abs = _yesterday_abs_return_pct(close)
    if y_abs > params["cooldown_absret_max"]:
        return {**decision, "final_signal": "HOLD", "rule": f"{rule}+M4:block_cooldown(|ret|={y_abs:.2f}%)"}
    rule = f"{rule}+M4:cooldown_ok(|ret|={y_abs:.2f}%)"

    # FINAL
    return {
        **decision,
        "final_signal": base,
        "rule": rule,
        "prob_down": round(prob_down, 4),
    }
