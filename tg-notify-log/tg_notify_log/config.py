"""конфигурация библиотеки tg-notify-log"""

from __future__ import annotations
from typing import Literal, Sequence
from pydantic import BaseModel, Field, SecretStr, field_validator

ParseMode = Literal["HTML", "MarkdownV2", "Markdown"] | None

class TgConfig(BaseModel):
    """Все настройки нотификатора в одном объекте"""

    model_config = {"frozen": True, "extra": "forbid"}

    token: SecretStr
    chat_id: int | str
    parse_mode: ParseMode = "HTML"
    disable_notification: bool = False
    disable_web_page_preview: bool = True
    protect_content: bool = False
    message_thread_id: int | None = None
    rate_limit_per_minute: int = Field(default=20, ge=1, le=600)
    dedup_window_seconds: int = Field(default=60, ge=0, le=3600)

    only_levels: Sequence[str] = Field(
        default_factory=lambda: ["ERROR", "CRITICAL"]
    )
    max_message_length: int = Field(default=4096, ge=100, le=4096)
    truncate_traceback: int = Field(default=3000, ge=100, le=10000)

    app_name: str = "app"
    include_env: Sequence[str] = Field(default_factory=list)
    include_hostname: bool = True
    include_process: bool = True

    silent_fail: bool = True
    retry_attempts: int = Field(default=3, ge=0, le=10)
    request_timeout: float = Field(default=10.0, gt=0, le=60)

    @field_validator("only_levels")
    @classmethod
    def _upper_levels(cls, v: Sequence[str]) -> Sequence[str]:
        return [str(x).upper() for x in v]

    @field_validator("app_name")
    @classmethod
    def _non_empty_app(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("app_name не может быть пустым")
        return v.strip()
