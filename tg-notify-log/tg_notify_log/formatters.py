"""форматирование сообщений для телеграм"""

from __future__ import annotations
import html
import os
import platform
import socket
import traceback
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

LEVEL_EMOJI: dict[str, str] = {
    "DEBUG": "🔍",
    "INFO": "ℹ️",
    "WARNING": "⚠️",
    "ERROR": "❌",
    "CRITICAL": "🔥",
}

def escape_html(text: str) -> str:
    """экранирует спецсимволы, но оставляет наши теги целыми"""
    return html.escape(str(text), quote=False)

def format_traceback(exc: BaseException | None, limit: int = 3000) -> str:
    """форматирует трейсбек в HTML <pre><code>"""
    if exc is None:
        return ""
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    if len(tb) > limit:
        tb = tb[:limit] + f"\n… (обрезано, всего {len(tb)} символов)"
    return (
        "<pre><code class=\"language-python\">"
        f"{escape_html(tb)}"
        "</code></pre>"
    )

def format_context(
    extra: Mapping[str, Any] | None = None,
    env_keys: Sequence[str] = (),
    *,
    include_hostname: bool = True,
    include_process: bool = True,
) -> str:
    """формирует блок с контекстом: хост, PID, Python, env, extra"""
    lines: list[str] = []

    if include_hostname:
        try:
            lines.append(f"🖥 <b>Хост:</b> <code>{escape_html(socket.gethostname())}</code>")
        except OSError:
            pass

    if include_process:
        lines.append(f"⚙️ <b>PID:</b> <code>{os.getpid()}</code>")
        lines.append(f"🐍 <b>Python:</b> <code>{platform.python_version()}</code>")

    for key in env_keys:
        val = os.getenv(key, "—")
        lines.append(f"🔑 <b>{escape_html(key)}:</b> <code>{escape_html(val)}</code>")

    if extra:
        for k, v in extra.items():
            lines.append(f"📌 <b>{escape_html(str(k))}:</b> <code>{escape_html(str(v))}</code>")

    return "\n".join(lines)

def build_message(
    level: str,
    message: str,
    *,
    exc: BaseException | None = None,
    extra: Mapping[str, Any] | None = None,
    env_keys: Sequence[str] = (),
    include_hostname: bool = True,
    include_process: bool = True,
    app_name: str = "app",
    traceback_limit: int = 3000,
    timestamp: bool = True,
    custom_template: str | None = None,
) -> str:
    """
    Собирает финальный HTML-текст сообщения.

    Если передан ``custom_template``, используются плейсхолдеры:
    ``{emoji} {level} {app} {ts} {message} {traceback} {context}``
    """
    level_up = str(level).upper()
    emoji = LEVEL_EMOJI.get(level_up, "📢")
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")

    context = format_context(
        extra,
        env_keys,
        include_hostname=include_hostname,
        include_process=include_process,
    )
    tb = format_traceback(exc, traceback_limit)

    if custom_template:
        return custom_template.format(
            emoji=emoji,
            level=level_up,
            app=escape_html(app_name),
            ts=ts,
            message=escape_html(message),
            traceback=tb,
            context=context,
        )

    parts: list[str] = []
    header = f"{emoji} <b>{escape_html(level_up)}</b>"
    if timestamp:
        header += f" · <i>{ts}</i>"
    header += f" · <code>{escape_html(app_name)}</code>"
    parts.append(header)
    parts.append("")
    parts.append(escape_html(message))

    if context:
        parts.append("")
        parts.append(context)

    if tb:
        parts.append("")
        parts.append("🧵 <b>Traceback:</b>")
        parts.append(tb)

    return "\n".join(parts)
