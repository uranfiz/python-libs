"""тесты форматирования сообщений"""

from __future__ import annotations
from tg_notify_log.formatters import (
    build_message,
    escape_html,
    format_context,
    format_traceback,
)

def test_escape_html() -> None:
    assert escape_html("<b>hi</b>") == "&lt;b&gt;hi&lt;/b&gt;"
    assert escape_html("a & b") == "a &amp; b"

def test_format_traceback_none() -> None:
    assert format_traceback(None) == ""

def test_format_traceback_has_code() -> None:
    try:
        1 / 0
    except ZeroDivisionError as exc:
        tb = format_traceback(exc)
    assert "<pre><code" in tb
    assert "ZeroDivisionError" in tb

def test_format_context_env(monkeypatch) -> None:
    monkeypatch.setenv("MY_SECRET", "value")
    ctx = format_context(None, ["MY_SECRET"], include_hostname=False, include_process=False)
    assert "MY_SECRET" in ctx
    assert "value" in ctx

def test_build_message_basic() -> None:
    msg = build_message("ERROR", "boom", include_hostname=False, include_process=False)
    assert "ERROR" in msg
    assert "boom" in msg

def test_build_message_custom_template() -> None:
    tpl = "[{level}] {message}"
    msg = build_message("WARNING", "hi", custom_template=tpl)
    assert msg == "[WARNING] hi"

def test_build_message_truncates_traceback() -> None:
    try:
        raise ValueError("x" * 5000)
    except ValueError as exc:
        msg = build_message(
            "ERROR", "boom", exc=exc, traceback_limit=100,
            include_hostname=False, include_process=False,
        )
    assert "обрезано" in msg
