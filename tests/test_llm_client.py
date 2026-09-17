import pytest

from agents.llm_client import ModelCallError, parse_structured_response


def test_parses_clean_json() -> None:
    result = parse_structured_response('{"recommendation": "BUY", "conviction": 7.5}')
    assert result == {"recommendation": "BUY", "conviction": 7.5}


def test_parses_json_with_surrounding_text() -> None:
    raw = 'Sure, here is my analysis:\n{"recommendation": "SELL", "conviction": 3}\nLet me know if you need more.'
    result = parse_structured_response(raw)
    assert result["recommendation"] == "SELL"
    assert result["conviction"] == 3


def test_raises_on_no_json() -> None:
    with pytest.raises(ModelCallError):
        parse_structured_response("I recommend buying this stock.")


def test_raises_on_malformed_json() -> None:
    with pytest.raises(ModelCallError):
        parse_structured_response('{"recommendation": "BUY", "conviction": }')
