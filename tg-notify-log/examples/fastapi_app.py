"""пример интеграции с FastAPI (async)"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from tg_notify_log import TgNotifyLog

app = FastAPI()

log = TgNotifyLog(
    token="123:ABC",
    chat_id=-1001234567890,
    app_name="fastapi-app",
    level="ERROR",
)

@app.get("/")
async def index() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/boom")
async def boom() -> dict[str, str]:
    1 / 0
    return {"status": "unreachable"}

@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception) -> JSONResponse:
    await log.aerror(
        f"{request.method} {request.url.path} упал",
        exc=exc,
        extra={"client": request.client.host if request.client else "unknown"},
        buttons=[("📄 Логи", f"https://kibana.example.com?path={request.url.path}")],
    )
    return JSONResponse({"error": "internal"}, status_code=500)
