"""тесты ядра TgNotifyLog (без реальных запросов к Telegram)"""

from __future__ import annotations
from typing import Any
from unittest.mock import patch
import pytest
from tg_notify_log import TgNotifyLog
from tg_notify_log.exceptions import TgNotifyConfigError

@pytest.fixture()
def fake_response() -> dict[str, Any]:
    return {"ok": True, "result": {"message_id": 1}}

@pytest.fixture()
def log(monkeypatch: pytest.MonkeyPatch, fake_response: dict[str, Any]) -> TgNotifyLog:
    def fake_send(self: Any, **payload: Any) -> dict[str, Any]:
        return fake_response

    monkeypatch.setattr(
        "tg_notify_log.client.TgClient.send_message",
        fake_send,
        raising=True,
    )
    return TgNotifyLog(token="123:ABC", chat_id=-100, level="DEBUG")

def test_bad_token_raises() -> None:
    with pytest.raises(ValueError):
        TgNotifyLog(token="nope", chat_id=1)

def test_level_filter(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tg_notify_log.client.TgClient.send_message",
        lambda self, **kw: {"ok": True},
        raising=True,
    )
    log = TgNotifyLog(token="123:ABC", chat_id=1, level="ERROR")
    assert log.info("nope") is None
    assert log.error("yes") == {"ok": True}

def test_dedup_skips_duplicates(log: TgNotifyLog) -> None:
    r1 = log.error("same message")
    r2 = log.error("same message")
    assert r1 is not None
    assert r2 is None

def test_repr_hides_token() -> None:
    log = TgNotifyLog(token="123:ABC", chat_id=-100)
    assert "123" not in repr(log)
    assert "ABC" not in repr(log)
    assert "***" in repr(log)

def test_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TGNL_TOKEN", "123:ABC")
    monkeypatch.setenv("TGNL_CHAT_ID", "-100")
    monkeypatch.setenv("TGNL_APP_NAME", "test-app")
    log = TgNotifyLog.from_env()
    assert log.cfg.app_name == "test-app"
    assert log.cfg.chat_id == "-100"

def test_from_env_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TGNL_TOKEN", raising=False)
    monkeypatch.delenv("TGNL_CHAT_ID", raising=False)
    with pytest.raises(TgNotifyConfigError):
        TgNotifyLog.from_env()

def test_from_dict() -> None:
    log = TgNotifyLog.from_dict(
        {"token": "123:ABC", "chat_id": -100, "app_name": "dict-app"}
    )
    assert log.cfg.app_name == "dict-app"

def test_buttons_passed_to_payload(log: TgNotifyLog) -> None:
    captured: dict[str, Any] = {}

    def capture(self: Any, **payload: Any) -> dict[str, Any]:
        captured.update(payload)
        return {"ok": True}

    with patch("tg_notify_log.client.TgClient.send_message", capture):
        log.error("with btn", buttons=[("Retry", "retry")])

    assert "reply_markup" in captured
    assert captured["reply_markup"]["inline_keyboard"][0][0]["callback_data"] == "retry"
