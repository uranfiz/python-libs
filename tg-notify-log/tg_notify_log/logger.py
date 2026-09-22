"""ядро tg-notify-log: класс TgNotifyLog"""

from __future__ import annotations
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from pydantic import ValidationError
from .buttons import ButtonSpec, build_keyboard
from .client import TgClient
from .config import TgConfig
from .exceptions import TgNotifyConfigError
from .formatters import build_message
from .rate_limit import Deduplicator, TokenBucket

HookFn = Callable[
    [str, str, dict[str, Any]],
    "tuple[str, dict[str, Any]] | None",
]

ENV_PREFIX = "TGNL_"
_ENV_MAP = {
    "TGNL_TOKEN": "token",
    "TGNL_CHAT_ID": "chat_id",
    "TGNL_PARSE_MODE": "parse_mode",
    "TGNL_APP_NAME": "app_name",
    "TGNL_LEVEL": "level", 
    "TGNL_RATE_LIMIT": "rate_limit_per_minute",
    "TGNL_DEDUP_WINDOW": "dedup_window_seconds",
    "TGNL_INCLUDE_ENV": "include_env",
    "TGNL_INCLUDE_HOSTNAME": "include_hostname",
    "TGNL_INCLUDE_PROCESS": "include_process",
    "TGNL_MESSAGE_THREAD_ID": "message_thread_id",
}

class TgNotifyLog:
    """
    Очень гибкий Telegram-логгер.

    Быстрый старт::

        from tg_notify_log import TgNotifyLog

        log = TgNotifyLog(token="123:ABC", chat_id=-1001234567890)
        log.error("Что-то сломалось", buttons=[("🔄 Retry", "retry")])

    Продакшн::

        log = TgNotifyLog.from_env()          # читает TGNL_TOKEN, TGNL_CHAT_ID, ...
        log = TgNotifyLog.from_file("config.toml")
    """

    def __init__(
        self,
        token: str,
        chat_id: int | str,
        *,
        level: str | int = "ERROR",
        parse_mode: str | None = "HTML",
        app_name: str = "app",
        include_env: Sequence[str] = (),
        include_hostname: bool = True,
        include_process: bool = True,
        rate_limit_per_minute: int = 20,
        dedup_window_seconds: int = 60,
        message_thread_id: int | None = None,
        max_message_length: int = 4096,
        truncate_traceback: int = 3000,
        disable_notification: bool = False,
        disable_web_page_preview: bool = True,
        protect_content: bool = False,
        silent_fail: bool = True,
        retry_attempts: int = 3,
        request_timeout: float = 10.0,
        buttons_columns: int = 1,
        custom_template: str | None = None,
        hooks: Sequence[HookFn] = (),
    ) -> None:
        try:
            self.cfg = TgConfig(
                token=token,
                chat_id=chat_id,
                parse_mode=parse_mode,
                app_name=app_name,
                include_env=list(include_env),
                include_hostname=include_hostname,
                include_process=include_process,
                rate_limit_per_minute=rate_limit_per_minute,
                dedup_window_seconds=dedup_window_seconds,
                message_thread_id=message_thread_id,
                max_message_length=max_message_length,
                truncate_traceback=truncate_traceback,
                disable_notification=disable_notification,
                disable_web_page_preview=disable_web_page_preview,
                protect_content=protect_content,
                silent_fail=silent_fail,
                retry_attempts=retry_attempts,
                request_timeout=request_timeout,
            )
        except ValidationError as exc:
            raise TgNotifyConfigError(str(exc)) from exc

        self._client = TgClient(
            token.get_secret_value() if hasattr(token, "get_secret_value") else str(token),
            timeout=request_timeout,
            retry_attempts=retry_attempts,
        )
        self._bucket = TokenBucket(rate_limit_per_minute)
        self._dedup = Deduplicator(dedup_window_seconds)
        self._min_level = self._normalize_level(level)
        self._buttons_columns = buttons_columns
        self._custom_template = custom_template
        self._hooks = list(hooks)
        self._internal_logger = logging.getLogger("tg_notify_log")

    @classmethod
    def from_env(
        cls,
        prefix: str = ENV_PREFIX,
        **overrides: Any,
    ) -> "TgNotifyLog":
        """
        Создаёт логгер из переменных окружения.

        Читает: TGNL_TOKEN, TGNL_CHAT_ID, TGNL_APP_NAME, TGNL_LEVEL,
        TGNL_RATE_LIMIT, TGNL_DEDUP_WINDOW, TGNL_INCLUDE_ENV и т.д.

        Args:
            prefix: префикс переменных (по умолчанию ``TGNL_``).
            **overrides: любые параметры, которые надо переопределить.
        """
        kwargs: dict[str, Any] = {}

        for env_key, field in _ENV_MAP.items():
            env_value = os.getenv(env_key if prefix == ENV_PREFIX else env_key.replace(ENV_PREFIX, prefix))
            if env_value is None:
                continue

            if field in ("include_env",):
                kwargs[field] = [x.strip() for x in env_value.split(",") if x.strip()]
            elif field in ("include_hostname", "include_process"):
                kwargs[field] = env_value.lower() in ("1", "true", "yes", "on")
            elif field in (
                "rate_limit_per_minute",
                "dedup_window_seconds",
                "message_thread_id",
            ):
                try:
                    kwargs[field] = int(env_value)
                except ValueError:
                    continue
            else:
                kwargs[field] = env_value

        kwargs.update(overrides)

        if "token" not in kwargs or "chat_id" not in kwargs:
            raise TgNotifyConfigError(
                f"Не найдены обязательные переменные: "
                f"{prefix}TOKEN и {prefix}CHAT_ID"
            )

        return cls(**kwargs)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], **overrides: Any) -> "TgNotifyLog":
        """создаёт логгер из словаря (например, распарсенного TOML/YAML)"""
        merged = dict(data)
        merged.update(overrides)
        return cls(**merged)

    @classmethod
    def from_file(cls, path: str | Path, **overrides: Any) -> "TgNotifyLog":
        """создаёт логгер из TOML-файла (поддерживается Python 3.11+)"""
        path = Path(path)
        if not path.is_file():
            raise TgNotifyConfigError(f"Файл конфигурации не найден: {path}")

        try:
            import tomllib
        except ModuleNotFoundError as exc:
            raise TgNotifyConfigError(
                "Для from_file требуется Python 3.11+ (модуль tomllib)"
            ) from exc

        with path.open("rb") as fh:
            data = tomllib.load(fh)

        section = data.get("tg_notify_log") or data.get("tg-notify-log") or data
        return cls.from_dict(section, **overrides)

    def debug(self, msg: str, **kwargs: Any) -> dict[str, Any] | None:
        return self._emit("DEBUG", msg, **kwargs)

    def info(self, msg: str, **kwargs: Any) -> dict[str, Any] | None:
        return self._emit("INFO", msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> dict[str, Any] | None:
        return self._emit("WARNING", msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> dict[str, Any] | None:
        return self._emit("ERROR", msg, **kwargs)

    def critical(self, msg: str, **kwargs: Any) -> dict[str, Any] | None:
        return self._emit("CRITICAL", msg, **kwargs)

    def exception(self, msg: str, **kwargs: Any) -> dict[str, Any] | None:
        """Автоматически подхватывает активный traceback (из except)."""
        kwargs.setdefault("exc", sys.exc_info()[1])
        return self._emit("ERROR", msg, **kwargs)

    async def aerror(self, msg: str, **kwargs: Any) -> dict[str, Any] | None:
        return await self._aemit("ERROR", msg, **kwargs)

    async def acritical(self, msg: str, **kwargs: Any) -> dict[str, Any] | None:
        return await self._aemit("CRITICAL", msg, **kwargs)

    def close(self) -> None:
        self._client.close()

    async def aclose(self) -> None:
        await self._client.aclose()

    @staticmethod
    def _normalize_level(level: str | int) -> int:
        if isinstance(level, int):
            return level
        return getattr(logging, str(level).upper(), logging.ERROR)

    def _should_send(self, level: str) -> bool:
        return getattr(logging, level.upper(), 0) >= self._min_level

    def _prepare_payload(
        self,
        level: str,
        message: str,
        kw: dict[str, Any],
    ) -> dict[str, Any] | None:
        text = build_message(
            level,
            message,
            exc=kw.get("exc"),
            extra=kw.get("extra"),
            env_keys=self.cfg.include_env,
            include_hostname=self.cfg.include_hostname,
            include_process=self.cfg.include_process,
            app_name=self.cfg.app_name,
            traceback_limit=self.cfg.truncate_traceback,
            custom_template=self._custom_template,
        )

        if len(text) > self.cfg.max_message_length:
            text = text[: self.cfg.max_message_length - 20] + "\n… (обрезано)"

        for hook in self._hooks:
            try:
                result = hook(level, text, kw)
            except Exception as hook_exc:  # noqa: BLE001
                self._internal_logger.warning("Хук упал: %s", hook_exc)
                continue
            if result is None:
                return None
            text, kw = result

        payload: dict[str, Any] = {
            "chat_id": self.cfg.chat_id,
            "text": text,
            "parse_mode": self.cfg.parse_mode,
            "disable_notification": self.cfg.disable_notification,
            "disable_web_page_preview": self.cfg.disable_web_page_preview,
            "protect_content": self.cfg.protect_content,
        }
        if self.cfg.message_thread_id:
            payload["message_thread_id"] = self.cfg.message_thread_id

        kb = build_keyboard(kw.get("buttons"), columns=self._buttons_columns)
        if kb:
            payload["reply_markup"] = kb

        return payload

    def _emit(self, level: str, message: str, **kw: Any) -> dict[str, Any] | None:
        if not self._should_send(level):
            return None

        if not self._bucket.allow():
            self._internal_logger.warning(
                "Rate limit: сообщение уровня %s отброшено", level
            )
            return None

        payload = self._prepare_payload(level, message, kw)
        if payload is None:
            return None

        if self._dedup.is_duplicate(payload["text"]):
            self._internal_logger.debug(
                "Дедупликация: пропущено сообщение уровня %s", level
            )
            return None

        result = self._client.send_message(**payload)
        if result is None and not self.cfg.silent_fail:
            raise RuntimeError("Не удалось отправить сообщение в Telegram")
        return result

    async def _aemit(
        self, level: str, message: str, **kw: Any
    ) -> dict[str, Any] | None:
        if not self._should_send(level):
            return None

        if not self._bucket.allow():
            self._internal_logger.warning(
                "Rate limit: async-сообщение уровня %s отброшено", level
            )
            return None

        payload = self._prepare_payload(level, message, kw)
        if payload is None:
            return None

        if self._dedup.is_duplicate(payload["text"]):
            return None

        result = await self._client.asend_message(**payload)
        if result is None and not self.cfg.silent_fail:
            raise RuntimeError("Не удалось отправить сообщение в Telegram (async)")
        return result

    def __repr__(self) -> str:
        return (
            f"TgNotifyLog(chat_id={self.cfg.chat_id!r}, "
            f"app_name={self.cfg.app_name!r}, token=***)"
        )
