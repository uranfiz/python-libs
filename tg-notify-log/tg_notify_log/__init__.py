"""
tg-notify-log — очень гибкий Telegram-логгер для Python.

Быстрый старт::

    from tg_notify_log import TgNotifyLog

    log = TgNotifyLog(token="123:ABC", chat_id=-1001234567890)
    log.error("Что-то сломалось", buttons=[("🔄 Retry", "retry")])
"""

from .buttons import build_keyboard
from .formatters import build_message, format_traceback
from .handler import TgNotifyHandler
from .logger import TgNotifyLog

__version__ = "0.1.0"
__author__ = "uranfiz"
__license__ = "AGPL-3.0-or-later"

__all__ = [
    "TgNotifyLog",
    "TgNotifyHandler",
    "build_keyboard",
    "build_message",
    "format_traceback",
    "__version__",
]
