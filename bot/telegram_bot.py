import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

from analysis.signal_generator import generate_signal
from analysis.news_analyzer import analyze_news
from analysis.technical_analyzer import get_technical_analysis
from utils.helpers import format_signal_result
from config.config import PREMIUM_IDS

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SUMMARY_CHAT_ID = os.getenv("SUMMARY_CHAT_ID")

# Komutlar
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    msg = (
        "🛰️ Welcome to Coinspace!\nUse /help to see available commands.\n\n"
        f"👤 *Your Chat ID:* `{user_id}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Welcome message\n"
        "/help - Command list\n"
        "/analyze COIN - Full analysis\n"
        "/news COIN - News analysis only\n"
        "/tech COIN - Technical analysis only\n"
        "/signal COIN - Signal summary\n"
        "/satinal - 💎 VIP Access – Unlock Full Power"
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Please provide a coin symbol (e.g., /analyze BTCUSDT).")
        return

    signal_result = generate_signal(coin)
    news_result = analyze_news(coin)
    tech_result = get_technical_analysis(coin)

    message = (
        f"🧠 News Sentiment: {news_result['sentiment']}\n"
        + "\n".join([f"- {h}" for h in news_result['headlines']]) + "\n\n"
        f"📊 RSI: {tech_result['rsi']}\n"
        f"📈 Technical Signal: {tech_result['signal']}\n\n"
        f"✅ Final Signal: {signal_result['final_signal']}"
    )

    await update.message.reply_text(message)

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Please provide a coin symbol (e.g., /news BTCUSDT).")
        return
    result = analyze_news(coin)
    msg = f"🧠 News Sentiment: {result['sentiment']}\n\n" + "\n".join([f"- {h}" for h in result['headlines']])
    await update.message.reply_text(msg)

async def tech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Please provide a coin symbol (e.g., /tech BTCUSDT).")
        return
    result = get_technical_analysis(coin)
    msg = f"📊 RSI: {result['rsi']}\n📈 Signal: {result['signal']}"
    await update.message.reply_text(msg)

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Please provide a coin symbol (e.g., /signal BTCUSDT).")
        return
    result = generate_signal(coin)
    await update.message.reply_text(f"✅ Final Signal: {result['final_signal']}")

async def satinal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💳 VIP Satın Al", url="https://your-payment-link.com")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "🎟 *Coinspace VIP Subscription Plans:*\n"
        "• 1 Month  – $29.99\n"
        "• 3 Months – $69.99\n"
        "• Lifetime – $299.99\n\n"
        "🪙 *Accepted Payments:*\n"
        "USDT (TRC20), BTC, DOGE\n\n"
        "🔐 VIP access is granted automatically after purchase."
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# Günlük Market Özeti
def get_market_summary():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        data = response.json()
        sorted_data = sorted(data, key=lambda x: float(x["priceChangePercent"]), reverse=True)
        top_gainers = sorted_data[:3]
        top_losers = sorted_data[-3:]
        return top_gainers, top_losers
    except Exception:
        return [], []

def format_market_summary(gainers, losers):
    message = "📊 *Daily Market Summary*\n\n"
    message += "🚀 *Top Gainers:*\n"
    for coin in gainers:
        message += f"• {coin['symbol']}: +{float(coin['priceChangePercent']):.2f}%\n"
    message += "\n📉 *Top Losers:*\n"
    for coin in losers:
        message += f"• {coin['symbol']}: {float(coin['priceChangePercent']):.2f}%\n"
    message += "\n🕘 This summary is sent daily at 21:00."
    return message

async def send_market_summary(app):
    gainers, losers = get_market_summary()
    message = format_market_summary(gainers, losers)
    if SUMMARY_CHAT_ID:
        await app.bot.send_message(chat_id=SUMMARY_CHAT_ID, text=message, parse_mode="Markdown")

# Bot Başlatıcı
def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("satinal", satinal))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: app.application.create_task(send_market_summary(app)), "cron", hour=21, minute=0)
    scheduler.start()

    print("🚀 Coinspace Bot is running...")
    app.run_polling()
