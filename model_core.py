import numpy as np

def run_model(df):
    """
    Einfaches Momentum-Modell:
    - 5-Tage vs 20-Tage Rendite
    """

    df = df.copy()
    df["ret"] = df["close"].pct_change()

    short = df["ret"].rolling(5).mean().iloc[-1]
    long = df["ret"].rolling(20).mean().iloc[-1]

    if np.isnan(short) or np.isnan(long):
        score = 0.0
    else:
        score = float(short - long)

    return {
        "score": score
    }
