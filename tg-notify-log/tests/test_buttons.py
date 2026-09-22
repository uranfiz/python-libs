"""тесты билдера инлайн-кнопок"""

from __future__ import annotations
import pytest
from tg_notify_log.buttons import build_keyboard

def test_none_when_empty() -> None:
    assert build_keyboard(None) is None
    assert build_keyboard([]) is None

def test_callback_vs_url() -> None:
    kb = build_keyboard([("Retry", "retry"), ("Docs", "https://example.com")])
    assert kb is not None
    row = kb["inline_keyboard"][0]
    assert row[0] == {"text": "Retry", "callback_data": "retry"}
    assert row[1] == {"text": "Docs", "url": "https://example.com"}

def test_tg_url_is_url() -> None:
    kb = build_keyboard([("Open", "tg://user?id=1")])
    assert kb is not None
    assert kb["inline_keyboard"][0][0] == {"text": "Open", "url": "tg://user?id=1"}

def test_columns() -> None:
    kb = build_keyboard([("A", "a"), ("B", "b"), ("C", "c")], columns=2)
    assert kb is not None
    rows = kb["inline_keyboard"]
    assert len(rows) == 2
    assert len(rows[0]) == 2
    assert len(rows[1]) == 1

def test_dict_spec() -> None:
    kb = build_keyboard(
        [{"text": "App", "web_app": {"url": "https://app.example.com"}}]
    )
    assert kb is not None
    assert kb["inline_keyboard"][0][0]["web_app"]["url"] == "https://app.example.com"

def test_bad_spec_raises() -> None:
    with pytest.raises(TypeError):
        build_keyboard([123]) 
    with pytest.raises(ValueError):
        build_keyboard([("A", "a", "b")])
    with pytest.raises(ValueError):
        build_keyboard([("", "x")])
