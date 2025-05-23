import os
from fastapi import FastAPI, Request
from telegram import Update
from bot.telegram_bot import telegram_app  # doğru import

from dotenv import load_dotenv
load_dotenv()

WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8000))

fastapi_app = FastAPI()

@fastapi_app.on_event("startup")
async def on_startup():
    await telegram_app.bot.set_webhook(WEBHOOK_URL)

@fastapi_app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return {"ok": True}
