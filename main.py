from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder
from config.config import TELEGRAM_TOKEN, WEBHOOK_URL
from bot.telegram_bot import setup_handlers

app = FastAPI()

application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
setup_handlers(application)

@app.on_event("startup")
async def startup():
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print("🚀 Webhook set. Coinspace Bot is ready.")

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()
    await application.process_update(update)
    return {"ok": True}
