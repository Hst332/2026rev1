import pandas as pd


def analyze_results(all_results):

    df = pd.DataFrame(all_results)

    if len(df) == 0:
        print("No results")
        return

    buy_df = df[df["signal"] == "BUY"]
    sell_df = df[df["signal"] == "SELL"]

    buy_winrate = (buy_df["future_return"] > 0).mean() * 100
    sell_winrate = (sell_df["future_return"] < 0).mean() * 100

    print()
    print(f"BUY WINRATE: {buy_winrate:.2f} %")
    print(f"SELL WINRATE: {sell_winrate:.2f} %")

    print("\nConfidence analysis:")

    bins = [(0.5,0.6),(0.6,0.7),(0.7,0.8),(0.8,0.9),(0.9,1.0)]

    for low, high in bins:
        subset = df[(df["prob_up"] >= low) & (df["prob_up"] < high)]
        winrate = (subset["future_return"] > 0).mean() * 100
        print(f"{low}-{high}: {winrate:.2f}% ({len(subset)} trades)")
