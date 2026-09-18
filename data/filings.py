"""Point-in-time SEC EDGAR filing loader.

Fixes the original paper's look-ahead risk for fundamentals the same way
data/prices.py does for prices: only a filing dated on or before `as_of` is
ever selected, even though EDGAR itself will happily serve anything.

Free, no API key — but SEC requires a descriptive User-Agent identifying the
requester (https://www.sec.gov/os/webmaster-faq#developers). Set
SEC_EDGAR_USER_AGENT in .env, e.g. "AlphaAgentsV2 research you@example.com".
Requests without one, or with a generic default, get rejected — there is no
safe placeholder to ship here.
"""

import os
import re
from dataclasses import dataclass
from datetime import date

import requests
from bs4 import BeautifulSoup

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:0>10}.json"
ARCHIVES_BASE = "https://www.sec.gov/Archives/edgar/data"

_ticker_to_cik_cache: dict[str, str] | None = None


def _user_agent() -> str:
    ua = os.environ.get("SEC_EDGAR_USER_AGENT")
    if not ua:
        raise RuntimeError(
            "SEC_EDGAR_USER_AGENT is not set. SEC requires a descriptive User-Agent "
            "with a contact, e.g. 'AlphaAgentsV2 research you@example.com' — set it "
            "in .env (see .env.example)."
        )
    return ua


def _get(url: str) -> requests.Response:
    resp = requests.get(url, headers={"User-Agent": _user_agent()}, timeout=20)
    resp.raise_for_status()
    return resp


def _ticker_to_cik(ticker: str) -> str:
    global _ticker_to_cik_cache
    if _ticker_to_cik_cache is None:
        data = _get(TICKER_MAP_URL).json()
        _ticker_to_cik_cache = {row["ticker"].upper(): str(row["cik_str"]) for row in data.values()}
    cik = _ticker_to_cik_cache.get(ticker.upper())
    if cik is None:
        raise ValueError(f"No CIK found for ticker {ticker!r}")
    return cik


@dataclass(frozen=True)
class Filing:
    ticker: str
    form: str  # "10-K" or "10-Q"
    filing_date: date
    accession_number: str
    primary_document: str
    cik: str

    @property
    def source_id(self) -> str:
        return f"SEC EDGAR:{self.ticker}:{self.form}:{self.filing_date.isoformat()}"

    @property
    def document_url(self) -> str:
        return f"{ARCHIVES_BASE}/{int(self.cik)}/{self.accession_number}/{self.primary_document}"


def select_latest_filing(
    ticker: str, cik: str, recent: dict, as_of: date, forms: tuple[str, ...] = ("10-K", "10-Q")
) -> Filing:
    """Pure selection logic over EDGAR's `filings.recent` structure — no I/O.

    Split out from find_latest_filing so the point-in-time cutoff logic is
    unit-testable without hitting the network.
    """
    candidates = []
    for i, form in enumerate(recent["form"]):
        if form not in forms:
            continue
        filing_date = date.fromisoformat(recent["filingDate"][i])
        if filing_date > as_of:
            continue
        candidates.append((filing_date, i, form))

    if not candidates:
        raise ValueError(f"No {'/'.join(forms)} filing found for {ticker} on or before {as_of}")

    filing_date, i, form = max(candidates, key=lambda c: c[0])
    accession = recent["accessionNumber"][i].replace("-", "")
    primary_doc = recent["primaryDocument"][i]

    return Filing(
        ticker=ticker.upper(),
        form=form,
        filing_date=filing_date,
        accession_number=accession,
        primary_document=primary_doc,
        cik=cik,
    )


def find_latest_filing(ticker: str, as_of: date, forms: tuple[str, ...] = ("10-K", "10-Q")) -> Filing:
    cik = _ticker_to_cik(ticker)
    submissions = _get(SUBMISSIONS_URL.format(cik=cik)).json()
    return select_latest_filing(ticker, cik, submissions["filings"]["recent"], as_of, forms)


def load_filing_text(filing: Filing, max_chars: int = 15000) -> str:
    """Plain text of the filing's primary document, truncated to max_chars.

    Modern filings are Inline XBRL: the same HTML document embeds a huge
    machine-readable metadata block (`<ix:header>`, namespace declarations,
    context refs like "P1Y") alongside the human-readable text. Naively
    extracting all text pulls in that metadata as noise ahead of the actual
    prose, so it's stripped explicitly before extraction.

    v1 simplification: takes the first max_chars of the remaining text
    rather than section-aware chunking (the "Financial Report RAG Tool"
    DESIGN.md describes as future work) — good enough to give the model
    real filing prose to reason over, not a substitute for real retrieval.
    """
    html = _get(filing.document_url).text
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.find_all(["ix:header", "ix:hidden", "script", "style"]):
        tag.decompose()
    for tag in soup.select('[style*="display:none"], [style*="display: none"]'):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:max_chars]
