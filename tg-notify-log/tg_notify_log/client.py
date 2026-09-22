"""низкоуровневый клиент Telegram Bot API для tg-notify-log"""

from __future__ import annotations
import asyncio
import logging
import time
from typing import Any
import httpx
from .exceptions import TgNotifySendError

logger = logging.getLogger("tg_notify_log.client")
_API_TEMPLATE = "https://api.telegram.org/bot{token}/{method}"

def _mask_token(token: str) -> str:
    """маскирует токен для логов: '123456:AAH...' → '1234**:***'"""
    if ":" in token:
        bot_id, _ = token.split(":", 1)
        return f"{bot_id[:4]}**:***"
    return "***"

class TgClient:
    """
    Обёртка над Telegram Bot API.

    Отправляет сообщения и документы. Хранит httpx-клиенты для sync и async,
    повторяет запросы при сетевых ошибках, маскирует токен в логах.
    """

    def __init__(
        self,
        token: str,
        *,
        timeout: float = 10.0,
        retry_attempts: int = 3,
        retry_backoff: float = 1.5,
    ) -> None:
        if not token or ":" not in token:
            raise ValueError(
                "Некорректный Telegram-токен. Ожидается формат '<bot_id>:<hash>'."
            )
        self._token = token
        self._timeout = timeout
        self._retry_attempts = retry_attempts
        self._retry_backoff = retry_backoff
        self._sync = httpx.Client(timeout=timeout)
        self._async: httpx.AsyncClient | None = None

    def _url(self, method: str) -> str:
        return _API_TEMPLATE.format(token=self._token, method=method)

    def _should_retry(self, exc: Exception) -> bool:
        if isinstance(exc, (httpx.TimeoutException, httpx.NetworkError)):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            code = exc.response.status_code
            return code == 429 or 500 <= code < 600
        return False

    def send_message(self, **payload: Any) -> dict[str, Any] | None:
        """синхронно отправляет сообщение. Возвращает ответ Telegram или None"""
        return self._request_sync("sendMessage", json=payload)

    def send_document(
        self,
        file: bytes | str,
        filename: str,
        **payload: Any,
    ) -> dict[str, Any] | None:
        """синхронно отправляет документ (bytes или путь к файлу)"""
        return self._request_sync(
            "sendDocument",
            data=payload,
            files={"document": (filename, file)},
        )

    def _request_sync(
        self,
        method: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        url = self._url(method)
        last_exc: Exception | None = None

        for attempt in range(self._retry_attempts + 1):
            try:
                resp = self._sync.post(url, json=json, data=data, files=files)
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                last_exc = exc
                if attempt < self._retry_attempts and self._should_retry(exc):
                    delay = self._retry_backoff ** attempt
                    logger.warning(
                        "Повтор запроса %s через %.1fs (попытка %d/%d, токен %s)",
                        method,
                        delay,
                        attempt + 1,
                        self._retry_attempts,
                        _mask_token(self._token),
                    )
                    time.sleep(delay)
                    continue
                break

        logger.error(
            "Не удалось выполнить %s (токен %s): %s",
            method,
            _mask_token(self._token),
            last_exc,
        )
        return None

    async def asend_message(self, **payload: Any) -> dict[str, Any] | None:
        """асинхронно отправляет сообщение"""
        return await self._request_async("sendMessage", json=payload)

    async def asend_document(
        self,
        file: bytes | str,
        filename: str,
        **payload: Any,
    ) -> dict[str, Any] | None:
        """асинхронно отправляет документ"""
        return await self._request_async(
            "sendDocument",
            data=payload,
            files={"document": (filename, file)},
        )

    async def _request_async(
        self,
        method: str,
        *,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if self._async is None:
            self._async = httpx.AsyncClient(timeout=self._timeout)

        url = self._url(method)
        last_exc: Exception | None = None

        for attempt in range(self._retry_attempts + 1):
            try:
                resp = await self._async.post(url, json=json, data=data, files=files)
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                last_exc = exc
                if attempt < self._retry_attempts and self._should_retry(exc):
                    delay = self._retry_backoff ** attempt
                    logger.warning(
                        "Повтор async-запроса %s через %.1fs (попытка %d/%d)",
                        method,
                        delay,
                        attempt + 1,
                        self._retry_attempts,
                    )
                    await asyncio.sleep(delay)
                    continue
                break

        logger.error(
            "Не удалось выполнить %s (токен %s): %s",
            method,
            _mask_token(self._token),
            last_exc,
        )
        return None

    def close(self) -> None:
        """закрывает синхронный клиент и, если есть, асинхронный"""
        try:
            self._sync.close()
        except Exception:
            pass

        if self._async is not None:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._async.aclose())
                else:
                    loop.run_until_complete(self._async.aclose())
            except Exception:
                pass
            self._async = None

    async def aclose(self) -> None:
        """асинхронно закрывает оба клиента"""
        try:
            self._sync.close()
        except Exception:
            pass
        if self._async is not None:
            await self._async.aclose()
            self._async = None

    def __enter__(self) -> "TgClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"TgClient(token={_mask_token(self._token)}, timeout={self._timeout})"
