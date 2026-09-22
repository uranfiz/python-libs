"""пример интеграции с Flask"""

from flask import Flask, jsonify
from tg_notify_log import TgNotifyLog

app = Flask(__name__)

log = TgNotifyLog(
    token="123:ABC",
    chat_id=-1001234567890,
    app_name="flask-app",
    level="ERROR",
    include_env=["FLASK_ENV"],
)

@app.route("/")
def index() -> str:
    return "ok"

@app.route("/boom")
def boom() -> tuple[str, int]:
    1 / 0
    return "unreachable", 200

@app.errorhandler(Exception)
def handle_error(exc: Exception):
    log.error(
        f"Flask упал: {exc!r}",
        exc=exc,
        buttons=[("📄 Логи", "https://kibana.example.com")],
    )
    return jsonify({"error": "internal"}), 500

if __name__ == "__main__":
    app.run(debug=True)
