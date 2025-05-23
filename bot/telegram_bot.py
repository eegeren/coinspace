import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from analysis.signal_generator import generate_signal
from analysis.news_analyzer import analyze_news
from analysis.technical_analyzer import get_technical_analysis
from utils.helpers import format_signal_result
from config.config import PREMIUM_IDS, SUMMARY_CHAT_ID

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Komutlar
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ /start komutu geldi")
    user_id = update.effective_chat.id
    msg = (
        "🛰️ Welcome to Coinspace!
Use /help to see available commands.

"
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
    price = signal_result.get("price", "N/A")

    message = (
        f"🧠 News Sentiment: {news_result['sentiment']}\n"
        + "\n".join([f"- {h}" for h in news_result['headlines']]) + "\n\n"
        f"📊 RSI: {tech_result['rsi']}\n"
        f"📈 Technical Signal: {tech_result['signal']}\n"
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
            f"\n💵 Current Price: {price}\n"
            "🔒 Unlock full entry/exit analysis and AI insights with /premium"
        )

    await update.message.reply_text(message, parse_mode="Markdown")

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

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    return message

async def send_market_summary(bot):
    gainers, losers = get_market_summary()
    message = format_market_summary(gainers, losers)
    if SUMMARY_CHAT_ID:
        await bot.send_message(chat_id=SUMMARY_CHAT_ID, text=message, parse_mode="Markdown")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gainers, losers = get_market_summary()
    message = format_market_summary(gainers, losers)
    await update.message.reply_text(message, parse_mode="Markdown")

async def realtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    is_premium = str(user_id) in PREMIUM_IDS
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        data = response.json()
        sorted_data = sorted(data, key=lambda x: abs(float(x["priceChangePercent"])), reverse=True)
        volatile_coins = sorted_data[:10]
        public_list = volatile_coins[:2]
        premium_list = volatile_coins[2:]
        message = "🌪 *Most Volatile Coins Today:*\n\n"
        for coin in public_list:
            message += f"• {coin['symbol']}: {float(coin['priceChangePercent']):.2f}%\n"
        if is_premium:
            message += "\n💎 *Premium Insights:*\n"
            for coin in premium_list:
                message += f"• {coin['symbol']}: {float(coin['priceChangePercent']):.2f}%\n"
        else:
            message += "\n🔒 Unlock 8 more coins with /premium"
        await update.message.reply_text(message, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text("⚠️ Couldn't fetch real-time data. Try again later.")

def setup_handlers(app: Application):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("premium", premium))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("realtime", realtime))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: app.create_task(send_market_summary(app.bot)), "cron", hour=21, minute=0)
    scheduler.start()

    print("✅ Handlers and scheduler loaded (Webhook mode)")
