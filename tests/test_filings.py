from datetime import date

import pytest

from data.filings import select_latest_filing

RECENT = {
    "form": ["10-Q", "10-K", "10-Q", "10-Q", "8-K"],
    "filingDate": ["2026-05-01", "2026-02-15", "2025-11-01", "2025-08-01", "2026-06-01"],
    "accessionNumber": ["0001-25-1", "0001-25-2", "0001-25-3", "0001-25-4", "0001-25-5"],
    "primaryDocument": ["q1.htm", "k.htm", "q4.htm", "q3.htm", "current.htm"],
}


def test_selects_most_recent_filing_on_or_before_as_of() -> None:
    filing = select_latest_filing("AAPL", "0000320193", RECENT, as_of=date(2026, 5, 15))
    assert filing.form == "10-Q"
    assert filing.filing_date == date(2026, 5, 1)
    assert filing.primary_document == "q1.htm"


def test_excludes_filings_after_as_of() -> None:
    filing = select_latest_filing("AAPL", "0000320193", RECENT, as_of=date(2026, 3, 1))
    assert filing.filing_date == date(2026, 2, 15)
    assert filing.form == "10-K"


def test_ignores_non_matching_forms() -> None:
    # 8-K filed 2026-06-01 is the most recent overall but isn't 10-K/10-Q.
    filing = select_latest_filing("AAPL", "0000320193", RECENT, as_of=date(2026, 6, 1))
    assert filing.form == "10-Q"
    assert filing.filing_date == date(2026, 5, 1)


def test_raises_when_no_filing_exists_before_as_of() -> None:
    with pytest.raises(ValueError):
        select_latest_filing("AAPL", "0000320193", RECENT, as_of=date(2020, 1, 1))


def test_accession_number_dashes_stripped() -> None:
    filing = select_latest_filing("AAPL", "0000320193", RECENT, as_of=date(2026, 5, 15))
    assert filing.accession_number == "0001251"
    assert "-" not in filing.accession_number
