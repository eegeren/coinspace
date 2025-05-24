import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SUMMARY_CHAT_ID = os.getenv("SUMMARY_CHAT_ID")

# Configuration settings
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

# Premium kullanıcıların Telegram ID'leri
PREMIUM_IDS = ["1916984442","974297341"]
