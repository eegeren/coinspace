import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder
from bot.telegram_bot import setup_handlers
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = FastAPI()

application = ApplicationBuilder().token(TOKEN).build()
setup_handlers(application)

@app.on_event("startup")
async def on_startup():
    await application.bot.set_webhook(url=WEBHOOK_URL)

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}
