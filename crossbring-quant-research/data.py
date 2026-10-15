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
    if os.path.exists(path) and not refresh:
        return pd.read_csv(path, index_col=0, parse_dates=True)
    tickers = OMXS30_TICKERS + [INDEX_TICKER]
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    close = raw["Close"].copy()
    # Drop tickers with too much missing history (delisted / renamed).
    keep = close.columns[close.notna().mean() > 0.95]
    close = close[keep].ffill().dropna(how="all")
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
    close.to_csv(path)
    return close
