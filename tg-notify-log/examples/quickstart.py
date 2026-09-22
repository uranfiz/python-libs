"""быстрый старт tg-notify-log"""

from tg_notify_log import TgNotifyLog

log = TgNotifyLog(
    token="123:ABC",              # замените на свой токен от @BotFather
    chat_id=-1001234567890,       # замените на ID своего чата
    app_name="quickstart",
    level="DEBUG",
)

log.debug("Отладочное сообщение")
log.info("Просто информация")
log.warning("Что-то подозрительное")
log.error("Ошибка!")
log.critical("Всё плохо!")

# с кнопками
log.error(
    "Сервис упал",
    extra={"region": "eu-1"},
    buttons=[
        ("🔄 Restart", "restart"),
        ("📊 Grafana", "https://grafana.example.com/d/abc"),
        ({"text": "🕹 WebApp", "web_app": {"url": "https://example.com/app"}}),
    ],
)

# с трейсбеком
try:
    1 / 0
except ZeroDivisionError:
    log.exception("Ошибка при расчёте корзины")
