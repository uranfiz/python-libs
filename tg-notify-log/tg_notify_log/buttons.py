"""билдер inline-кнопок для telegram"""

from __future__ import annotations
from typing import Any, Literal, Sequence, TypeAlias

ButtonSpec: TypeAlias = (
    tuple[str, str]
    | dict[str, Any]
)

InlineKeyboard: TypeAlias = dict[str, list[list[dict[str, Any]]]]

def _detect_kind(value: str) -> Literal["url", "callback_data"]:
    if value.startswith(("http://", "https://", "tg://")):
        return "url"
    return "callback_data"

def build_keyboard(
    buttons: Sequence[ButtonSpec] | None,
    *,
    columns: int = 1,
) -> InlineKeyboard | None:
    """
    Собирает InlineKeyboardMarkup из простых спек.

    Примеры::

        build_keyboard([("Retry", "retry"), ("Docs", "https://...")])
        build_keyboard([{"text": "App", "web_app": {"url": "https://..."}}])
    """
    if not buttons:
        return None
    if columns < 1:
        columns = 1

    rows: list[list[dict[str, Any]]] = []
    row: list[dict[str, Any]] = []

    for spec in buttons:
        if isinstance(spec, tuple):
            if len(spec) != 2:
                raise ValueError(f"Кортеж кнопки должен быть (text, value), получено: {spec!r}")
            text, value = spec
            if not isinstance(text, str) or not isinstance(value, str):
                raise TypeError("Оба элемента кортежа должны быть строками")
            if not text:
                raise ValueError("Текст кнопки не может быть пустым")
            kind = _detect_kind(value)
            btn: dict[str, Any] = {"text": text, kind: value}
        elif isinstance(spec, dict):
            btn = dict(spec)
            if "text" not in btn:
                raise ValueError(f"В кнопке-словаре нет 'text': {spec!r}")
        else:
            raise TypeError(f"Неподдерживаемый тип кнопки: {type(spec).__name__}")

        row.append(btn)
        if len(row) >= columns:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return {"inline_keyboard": rows}
