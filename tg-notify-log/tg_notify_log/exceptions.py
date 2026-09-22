"""Исключения tg-notify-log"""

from __future__ import annotations

class TgNotifyError(Exception):
    """базовое исключение библиотеки"""

class TgNotifyConfigError(TgNotifyError):
    """ошибка конфигурации (неверный токен, chat_id и тп)"""

class TgNotifySendError(TgNotifyError):
    """не удалось отправить сообщение в Telegram"""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code

class TgNotifyRateLimited(TgNotifyError):
    """сообщение отброшено из-за rate-limit"""
