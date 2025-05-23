import os
import requests
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

from analysis.signal_generator import generate_signal
from analysis.news_analyzer import analyze_news
from analysis.technical_analyzer import get_technical_analysis
from config.config import PREMIUM_IDS

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
SUMMARY_CHAT_ID = os.getenv("SUMMARY_CHAT_ID")

# Telegram bot uygulaması oluştur
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Komutlar
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    await update.message.reply_text(
        f"🛰️ Welcome to Coinspace!\nUse /help to see available commands.\n\n"
        f"👤 *Your Chat ID:* `{user_id}`",
        parse_mode="Markdown"
    )

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
        return await update.message.reply_text("⚠️ Please provide a coin symbol (e.g., /analyze BTCUSDT).")

    signal = generate_signal(coin)
    news = analyze_news(coin)
    tech = get_technical_analysis(coin)

    msg = (
        f"🧠 News Sentiment: {news['sentiment']}\n"
        + "\n".join([f"- {h}" for h in news['headlines']]) + "\n\n"
        f"📊 RSI: {tech['rsi']}\n"
        f"📈 Technical Signal: {tech['signal']}\n\n"
    )

    if is_premium:
        msg += (
            f"🔍 EMA Trend: {tech.get('ema_trend', 'N/A')}\n"
            f"📉 MACD: {tech.get('macd', 'N/A')}\n"
            f"🤖 AI Comment: {signal.get('ai_comment', 'N/A')}\n"
            f"📥 Entry: {signal.get('entry', 'N/A')}\n"
            f"🛑 Stop Loss: {signal.get('stop_loss', 'N/A')}\n"
            f"🎯 Take Profit: {signal.get('take_profit', 'N/A')}\n"
        )
    else:
        msg += f"✅ Final Signal: {signal['final_signal']}\n\n🔒 Unlock more details with /premium"

    await update.message.reply_text(msg, parse_mode="Markdown")

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        return await update.message.reply_text("⚠️ Please provide a coin symbol.")
    news = analyze_news(coin)
    msg = f"🧠 News Sentiment: {news['sentiment']}\n\n" + "\n".join([f"- {h}" for h in news['headlines']])
    await update.message.reply_text(msg)

async def tech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        return await update.message.reply_text("⚠️ Please provide a coin symbol.")
    tech = get_technical_analysis(coin)
    await update.message.reply_text(f"📊 RSI: {tech['rsi']}\n📈 Signal: {tech['signal']}")

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        return await update.message.reply_text("⚠️ Please provide a coin symbol.")
    signal = generate_signal(coin)
    await update.message.reply_text(f"✅ Final Signal: {signal['final_signal']}")

async def premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💳 VIP Satın Al", url="https://your-payment-link.com")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "🎟 *Coinspace VIP Plans:*\n"
        "• 1 Month – $29.99\n"
        "• 3 Months – $69.99\n"
        "• Lifetime – $299.99\n\n"
        "🪙 Payments: USDT (TRC20), BTC, DOGE"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

# Market Özeti
def get_market_summary():
    try:
        data = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
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
    g, l = get_market_summary()
    await update.message.reply_text(format_market_summary(g, l), parse_mode="Markdown")

async def realtime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    is_premium = str(user_id) in PREMIUM_IDS
    data = requests.get("https://api.binance.com/api/v3/ticker/24hr").json()
    sorted_data = sorted(data, key=lambda x: abs(float(x["priceChangePercent"])), reverse=True)
    public, premium_data = sorted_data[:2], sorted_data[2:10]
    msg = "🌪 *Top Volatile Coins Today:*\n"
    msg += "\n".join([f"• {c['symbol']}: {float(c['priceChangePercent']):.2f}%" for c in public])
    if is_premium:
        msg += "\n\n💎 *Premium Coins:*\n" + "\n".join([f"• {c['symbol']}: {float(c['priceChangePercent']):.2f}%" for c in premium_data])
    else:
        msg += "\n\n🔒 Unlock 8 more with /premium"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def send_market_summary(app):
    g, l = get_market_summary()
    if SUMMARY_CHAT_ID:
        await app.bot.send_message(chat_id=SUMMARY_CHAT_ID, text=format_market_summary(g, l), parse_mode="Markdown")

# Zamanlayıcı
scheduler = BackgroundScheduler()
scheduler.add_job(lambda: app.application.create_task(send_market_summary(app)), "cron", hour=21)
scheduler.start()

# Handler'ları ekle
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("analyze", analyze))
app.add_handler(CommandHandler("news", news))
app.add_handler(CommandHandler("tech", tech))
app.add_handler(CommandHandler("signal", signal))
app.add_handler(CommandHandler("summary", summary))
app.add_handler(CommandHandler("realtime", realtime))
app.add_handler(CommandHandler("premium", premium))

# Dışa aktarılacak: FastAPI tarafından çağrılacak
telegram_app = app
