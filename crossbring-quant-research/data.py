"""Download and cache daily OHLCV for a Swedish equity basket + OMXS30 index."""
from __future__ import annotations
import os
import pandas as pd
import yfinance as yf

# OMXS30-style basket (Nasdaq Stockholm, Yahoo tickers). A few names rotate in/out
# of the real index; this is a representative large-cap set, not the exact index.
OMXS30_TICKERS = [
    "ABB.ST", "ALFA.ST", "ASSA-B.ST", "ATCO-A.ST", "AZN.ST", "BOL.ST", "ELUX-B.ST",
    "ERIC-B.ST", "ESSITY-B.ST", "EVO.ST", "GETI-B.ST", "HEXA-B.ST", "HM-B.ST",
    "INVE-B.ST", "KINV-B.ST", "NDA-SE.ST", "NIBE-B.ST", "SAAB-B.ST", "SAND.ST",
    "SCA-B.ST", "SEB-A.ST", "SHB-A.ST", "SINCH.ST", "SKA-B.ST", "SKF-B.ST",
    "SWED-A.ST", "TEL2-B.ST", "TELIA.ST", "VOLV-B.ST", "LIFCO-B.ST", "EPI-A.ST",
]
INDEX_TICKER = "^OMX"
CACHE = os.path.join(os.path.dirname(__file__), "data_cache")


def load_prices(start: str, end: str | None = None, refresh: bool = False) -> pd.DataFrame:
    """Return adjusted close prices, one column per ticker, index = trading days."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f"prices_{start}_{end or 'latest'}.csv")
    cached = pd.read_csv(path, index_col=0, parse_dates=True) if os.path.exists(path) else None
    if cached is not None and not refresh:
        return cached
    tickers = OMXS30_TICKERS + [INDEX_TICKER]
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    close = raw["Close"].copy()
    # Drop tickers with too much missing history (delisted / renamed).
    keep = close.columns[close.notna().mean() > 0.95]
    close = close[keep].dropna(how="all")
    # A date where most stocks are missing is a feed gap, not a trading day. Yahoo has
    # been seen to drop a whole Stockholm session retroactively. Remove such rows instead
    # of forward-filling them, which would fake a zero-return day.
    stocks = [c for c in close.columns if c != INDEX_TICKER]
    close = close[close[stocks].isna().mean(axis=1) <= 0.5]
    close = close.ffill()
    # Drop a trailing partial bar only while the Stockholm market is still open.
    # Yahoo shows today's row with volume 0 for hours after the 17:30 close, so a
    # volume-based rule alone would leave the pipeline one day stale forever.
    from datetime import datetime
    from zoneinfo import ZoneInfo
    now_sthlm = datetime.now(ZoneInfo("Europe/Stockholm"))
    last_is_today = close.index[-1].date() == now_sthlm.date()
    market_open = (now_sthlm.hour, now_sthlm.minute) < (17, 45)
    if last_is_today and market_open and len(close) > 1:
        close = close.iloc[:-1]
    # Merge with the cache: fresh values win, but dates the feed has lost since the
    # last download are kept from the cache rather than erased.
    if cached is not None:
        close = close.combine_first(cached).sort_index()
    # A row where every stock equals the previous row is a forward-filled gap that got
    # into the cache before the guard above existed. Drop it.
    import numpy as np
    prev = close[stocks].shift(1)
    same = np.isclose(close[stocks].values, prev.values, rtol=1e-6).all(axis=1) & prev.notna().all(axis=1).values
    close = close[~same]
    close.to_csv(path)
    return close
