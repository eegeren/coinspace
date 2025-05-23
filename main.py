from fastapi import FastAPI, Request
from telegram.ext import ApplicationBuilder
from telegram import Update
import os, asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8000))

app = FastAPI()
tg_app = ApplicationBuilder().token(TOKEN).build()

@app.on_event("startup")
async def startup():
    await tg_app.bot.set_webhook(WEBHOOK_URL)

@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.update_queue.put(update)
    return {"ok": True}
