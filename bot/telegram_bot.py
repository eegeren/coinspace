import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from apscheduler.schedulers.background import BackgroundScheduler
from analysis.signal_generator import generate_signal
from analysis.news_analyzer import analyze_news
from analysis.technical_analyzer import get_technical_analysis
from utils.helpers import format_signal_result
from config.config import PREMIUM_IDS

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SUMMARY_CHAT_ID = os.getenv("SUMMARY_CHAT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # örnek: https://coinspace.onrender.com/webhook

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
        "/summary - Market Summary on Demand\n"
        "/realtime - Most Volatile Coins\n"
        "/premium - VIP Access – Unlock Full Power"
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    is_premium = str(user_id) in PREMIUM_IDS
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
    )
    if is_premium:
        message += (
            f"🔍 EMA Trend: {tech_result.get('ema_trend', 'N/A')}\n"
            f"📉 MACD: {tech_result.get('macd', 'N/A')}\n"
            f"🤖 AI Comment: {signal_result.get('ai_comment', 'N/A')}\n"
            f"📥 Entry Point: {signal_result.get('entry', 'N/A')}\n"
            f"🛑 Stop Loss: {signal_result.get('stop_loss', 'N/A')}\n"
            f"🎯 Take Profit: {signal_result.get('take_profit', 'N/A')}\n"
        )
    else:
        message += (
            f"✅ Final Signal: {signal_result['final_signal']}\n\n"
            "🔒 Unlock detailed analysis with /premium"
        )
    await update.message.reply_text(message)

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Please provide a coin symbol.")
        return
    result = analyze_news(coin)
    msg = f"🧠 News Sentiment: {result['sentiment']}\n\n" + "\n".join([f"- {h}" for h in result['headlines']])
    await update.message.reply_text(msg)

async def tech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Please provide a coin symbol.")
        return
    result = get_technical_analysis(coin)
    msg = f"📊 RSI: {result['rsi']}\n📈 Signal: {result['signal']}"
    await update.message.reply_text(msg)

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Please provide a coin symbol.")
        return
    result = generate_signal(coin)
    await update.message.reply_text(f"✅ Final Signal: {result['final_signal']}")

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💳 VIP Satın Al", url="https://your-payment-link.com")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "🎟 *Coinspace VIP Plans:*\n"
        "• 1 Month – $29.99\n"
        "• 3 Months – $69.99\n"
        "• Lifetime – $299.99\n\n"
        "🪙 Payments Accepted: USDT (TRC20), BTC, DOGE"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

def get_market_summary():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        data = response.json()
        sorted_data = sorted(data, key=lambda x: float(x["priceChangePercent"]), reverse=True)
        return sorted_data[:3], sorted_data[-3:]
    except:
        return [], []

def format_market_summary(gainers, losers):
    msg = "📊 *Daily Market Summary*\n\n🚀 *Top Gainers:*\n"
    msg += "\n".join([f"• {c['symbol']}: +{float(c['priceChangePercent']):.2f}%" for c in gainers])
    msg += "\n\n📉 *Top Losers:*\n"
    msg += "\n".join([f"• {c['symbol']}: {float(c['priceChangePercent']):.2f}%" for c in losers])
    return msg

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gainers, losers = get_market_summary()
    message = format_market_summary(gainers, losers)
    await update.message.reply_text(message, parse_mode="Markdown")

async def realtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    is_premium = str(user_id) in PREMIUM_IDS
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = sorted(response.json(), key=lambda x: abs(float(x["priceChangePercent"])), reverse=True)
    public = data[:2]
    premium = data[2:10]
    msg = "🌪 *Top Volatile Coins Today:*\n"
    msg += "\n".join([f"• {c['symbol']}: {float(c['priceChangePercent']):.2f}%" for c in public])
    if is_premium:
        msg += "\n\n💎 *Premium Coins:*\n"
        msg += "\n".join([f"• {c['symbol']}: {float(c['priceChangePercent']):.2f}%" for c in premium])
    else:
        msg += "\n\n🔒 Unlock more with /premium"
    await update.message.reply_text(msg, parse_mode="Markdown")

# Webhook ile başlat
def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("realtime", realtime))
    app.add_handler(CommandHandler("premium", premium))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: app.application.create_task(send_market_summary(app)), "cron", hour=21)
    scheduler.start()

    print("🚀 Coinspace Webhook Bot is running...")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        webhook_url=os.getenv("WEBHOOK_URL")

    )
