import os
import logging
from fastapi import FastAPI, Request
from bot.telegram_bot import build_bot_app  # ✅ DÜZELTİLDİ
from telegram.ext import Application
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "8000"))

bot_app: Application = build_bot_app()
fastapi_app = FastAPI()


@fastapi_app.on_event("startup")
async def on_startup():
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    logging.info("✅ Webhook set at %s", WEBHOOK_URL)


@fastapi_app.post(WEBHOOK_PATH)
async def handle_webhook(request: Request):
    update = await request.json()
    await bot_app.update_queue.put(update)
    return {"status": "ok"}
