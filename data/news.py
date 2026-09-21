"""Point-in-time news loader via Finnhub's company-news endpoint.

Fixes the original paper's look-ahead risk for news the same way
data/prices.py does for prices and data/filings.py does for filings: only
articles dated on or before `as_of` are ever returned, even though the
underlying API will happily serve a date range you didn't ask for if the
request is built carelessly.

Requires a free Finnhub API key (https://finnhub.io/register) set as
FINNHUB_API_KEY in .env. Left blank, the Sentiment Agent falls back to a
reduced feature set (see agents/sentiment.py) rather than failing outright,
per .env.example.
"""

import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

import requests

COMPANY_NEWS_URL = "https://finnhub.io/api/v1/company-news"


def _api_key() -> str:
    key = os.environ.get("FINNHUB_API_KEY")
    if not key:
        raise RuntimeError(
            "FINNHUB_API_KEY is not set. Register for a free key at "
            "https://finnhub.io/register and set it in .env (see .env.example)."
        )
    return key


@dataclass(frozen=True)
class NewsArticle:
    ticker: str
    headline: str
    summary: str
    source: str
    published: date
    url: str

    @property
    def source_id(self) -> str:
        return f"Finnhub:{self.ticker}:{self.source}:{self.published.isoformat()}"


def select_articles(raw: list[dict], ticker: str, as_of: date) -> list[NewsArticle]:
    """Pure filtering/parsing over Finnhub's raw company-news JSON — no I/O.

    Split out from load_company_news so the point-in-time cutoff logic is
    unit-testable without hitting the network, matching the pattern in
    data/filings.py's select_latest_filing.
    """
    articles = []
    for item in raw:
        published = datetime.fromtimestamp(item["datetime"], tz=timezone.utc).date()
        if published > as_of:
            continue
        if not item.get("headline"):
            continue
        articles.append(
            NewsArticle(
                ticker=ticker.upper(),
                headline=item["headline"],
                summary=item.get("summary", ""),
                source=item.get("source", "unknown"),
                published=published,
                url=item.get("url", ""),
            )
        )
    articles.sort(key=lambda a: a.published, reverse=True)
    return articles


def load_company_news(ticker: str, as_of: date, lookback_days: int = 14) -> list[NewsArticle]:
    """Articles for `ticker` published on or before `as_of`, most recent first.

    Returns an empty list (not an error) when nothing is found in the
    lookback window — the Sentiment Agent's role prompt is written to report
    low conviction on thin coverage rather than treat it as a failure.
    """
    start = as_of - timedelta(days=lookback_days)
    resp = requests.get(
        COMPANY_NEWS_URL,
        params={
            "symbol": ticker.upper(),
            "from": start.isoformat(),
            "to": as_of.isoformat(),
            "token": _api_key(),
        },
        timeout=20,
    )
    resp.raise_for_status()
    return select_articles(resp.json(), ticker, as_of)
