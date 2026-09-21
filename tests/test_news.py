from datetime import date

from data.news import select_articles

RAW = [
    {"datetime": 1747699200, "headline": "AAPL beats Q1 estimates", "summary": "Strong iPhone sales.", "source": "Reuters", "url": "https://example.com/1"},  # 2025-05-20
    {"datetime": 1747872000, "headline": "AAPL announces buyback", "summary": "New $90B program.", "source": "Bloomberg", "url": "https://example.com/2"},  # 2025-05-22
    {"datetime": 1748044800, "headline": "AAPL faces antitrust probe", "summary": "EU regulators open inquiry.", "source": "WSJ", "url": "https://example.com/3"},  # 2025-05-24
    {"datetime": 1747785600, "headline": "", "summary": "Headline-less wire blurb.", "source": "Wire", "url": "https://example.com/4"},  # 2025-05-21, no headline
]


def test_excludes_articles_after_as_of() -> None:
    articles = select_articles(RAW, "AAPL", as_of=date(2025, 5, 22))
    headlines = {a.headline for a in articles}
    assert "AAPL faces antitrust probe" not in headlines
    assert "AAPL announces buyback" in headlines


def test_sorted_most_recent_first() -> None:
    articles = select_articles(RAW, "AAPL", as_of=date(2025, 5, 24))
    published = [a.published for a in articles]
    assert published == sorted(published, reverse=True)


def test_drops_items_without_a_headline() -> None:
    articles = select_articles(RAW, "AAPL", as_of=date(2025, 5, 24))
    assert all(a.headline for a in articles)
    assert len(articles) == 3


def test_empty_when_nothing_before_as_of() -> None:
    articles = select_articles(RAW, "AAPL", as_of=date(2020, 1, 1))
    assert articles == []


def test_source_id_format() -> None:
    articles = select_articles(RAW, "aapl", as_of=date(2025, 5, 24))
    article = next(a for a in articles if a.headline == "AAPL beats Q1 estimates")
    assert article.source_id == "Finnhub:AAPL:Reuters:2025-05-20"
