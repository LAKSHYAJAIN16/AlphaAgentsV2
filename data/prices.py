"""Point-in-time price/volume loading.

`as_of` filtering is what fixes the original paper's look-ahead risk for
price data: yfinance will happily return data past the requested date if
asked carelessly, so the cutoff is enforced explicitly here rather than
trusted to caller discipline.
"""

from datetime import date, timedelta

import pandas as pd
import yfinance as yf


def load_price_history(ticker: str, as_of: date, lookback_days: int = 180) -> pd.DataFrame:
    start = as_of - timedelta(days=lookback_days)
    df = yf.download(
        ticker,
        start=start.isoformat(),
        end=(as_of + timedelta(days=1)).isoformat(),
        progress=False,
        auto_adjust=True,
    )
    if df.empty:
        raise ValueError(f"No price data returned for {ticker} up to {as_of}")
    df = df[df.index.date <= as_of]
    if df.empty:
        raise ValueError(f"Price data for {ticker} exists but none on or before {as_of}")
    return df
