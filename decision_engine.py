"""Decision engine

Ziel:
- Aus dem Modell-"score" eine konsistente Wahrscheinlichkeit ableiten (prob_up/prob_down).
- Daraus Signal + Confidence berechnen.

Wichtig:
"score" aus model_core ist ein z-standardisierter Drift (kleine Werte, typ. -0.02 .. +0.02).
Darum wird er mit einem Scale in eine S-Kurve (tanh) gemappt.
"""

from __future__ import annotations

import math
from typing import Dict, Any


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def score_to_prob_up(score: float, scale: float = 150.0) -> float:
    """
    Map score -> prob_up in [0,1] via tanh.

    - score ~ 0 => prob_up ~ 0.5
    - positive score => prob_up > 0.5
    - negative score => prob_up < 0.5
    """
    x = math.tanh(score * scale)  # [-1,1]
    return _clamp(0.5 + 0.5 * x)


def generate_signal(model_output: Dict[str, Any], regime: str) -> Dict[str, Any]:
    score = float(model_output.get("score", 0.0))

    prob_up = score_to_prob_up(score)
    prob_down = 1.0 - prob_up

    # Confidence ist Abstand zu 50/50
    confidence = abs(prob_up - 0.5) * 2.0  # 0..1

    # Basissignal (Trade Filter entscheidet final!)
    if prob_up >= 0.55:
        signal = "BUY"
    elif prob_up <= 0.45:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "signal": signal,
        "confidence": round(confidence, 4),
        "prob_up": round(prob_up, 4),
        "prob_down": round(prob_down, 4),
        "score": round(score, 6),
        "regime": regime,
    }
