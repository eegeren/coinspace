import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder
from contextlib import asynccontextmanager
from bot.telegram_bot import setup_handlers

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

application = ApplicationBuilder().token(TOKEN).build()
setup_handlers(application)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await application.bot.set_webhook(url=WEBHOOK_URL)
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def handle_webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}
