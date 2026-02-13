import yfinance as yf
import pandas as pd


def _normalize_index(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure DatetimeIndex is tz-naive (fixes tz-naive vs tz-aware concat/sort errors)."""
    if df is None or df.empty:
        return df

    df = df.copy()

    if not isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index, errors="coerce")

    # If tz-aware -> convert to UTC then drop tz
    try:
        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_convert("UTC").tz_localize(None)
    except Exception:
        # Fallback: try to drop tz
        try:
            df.index = df.index.tz_localize(None)
        except Exception:
            pass

    df = df[~df.index.isna()]
    return df


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    yfinance kann Spalten als MultiIndex/tuples liefern, z.B. ('Close','^GDAXI').
    Wir flatten IMMER auf open/high/low/close/volume.
    """
    if df is None or df.empty:
        return df

    # MultiIndex -> first level
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [str(c[0]).lower() for c in df.columns]
    else:
        cols = []
        for c in df.columns:
            if isinstance(c, tuple):
                cols.append(str(c[0]).lower())
            else:
                cols.append(str(c).lower())
        df.columns = cols

    rename_map = {"adj close": "close"}
    df = df.rename(columns=rename_map)
    return df


def load_market_data(ticker: str, cfg=None) -> pd.DataFrame:
    print(f"Loading market data for {ticker}")

    df_intraday = yf.download(
        ticker,
        period="5d",
        interval="1h",
        auto_adjust=True,
        progress=False,
        threads=False,
        group_by="column",
    )

    df_daily = yf.download(
        ticker,
        period="1y",
        interval="1d",
        auto_adjust=True,
        progress=False,
        threads=False,
        group_by="column",
    )

    if (df_intraday is None or df_intraday.empty) and (df_daily is None or df_daily.empty):
        raise ValueError(f"No data for {ticker}")

    # IMPORTANT: normalize timezone BEFORE concatenation / sorting
    df_intraday = _normalize_index(df_intraday)
    df_daily = _normalize_index(df_daily)

    df_intraday = _normalize_columns(df_intraday)
    df_daily = _normalize_columns(df_daily)

    df = pd.concat([df_daily, df_intraday]).sort_index()
    df = df[~df.index.duplicated(keep="last")]

    required = {"open", "high", "low", "close"}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"{ticker}: Missing columns {missing}. Got columns: {list(df.columns)}")

    return df
