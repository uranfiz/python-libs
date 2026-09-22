"""logging.Handler, отправляющий ошибки в Telegram"""

from __future__ import annotations
import logging
from typing import Any, Sequence
from .buttons import ButtonSpec
from .logger import TgNotifyLog

class TgNotifyHandler(logging.Handler):
    """
    Отправляет записи логов в Telegram через TgNotifyLog.

    Пример::

        logging.basicConfig(
            handlers=[
                logging.StreamHandler(),
                TgNotifyHandler(token="...", chat_id=..., level=logging.ERROR),
            ],
        )
        logging.error("База упала")
    """

    def __init__(
        self,
        token: str,
        chat_id: int | str,
        *,
        level: int = logging.ERROR,
        buttons: Sequence[ButtonSpec] | None = None,
        notifier: TgNotifyLog | None = None,
        **notifier_kwargs: Any,
    ) -> None:
        super().__init__(level=level)

        self._notifier = notifier or TgNotifyLog(
            token=token,
            chat_id=chat_id,
            level=level,
            **notifier_kwargs,
        )
        self._buttons = buttons

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            exc = record.exc_info[1] if record.exc_info else None
            extra: dict[str, Any] = {
                "logger": record.name,
                "module": record.module,
                "line": record.lineno,
            }
            if record.exc_text:
                extra["exc_preview"] = record.exc_text[:200]

            self._notifier._emit(
                record.levelname,
                msg,
                exc=exc,
                extra=extra,
                buttons=self._buttons,
            )
        except Exception: 
            self.handleError(record)

    def close(self) -> None:
        try:
            self._notifier.close()
        finally:
            super().close()
