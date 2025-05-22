import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv
from analysis.signal_generator import generate_signal
from analysis.news_analyzer import analyze_news
from analysis.technical_analyzer import get_technical_analysis
from utils.helpers import format_signal_result
from config.config import PREMIUM_IDS

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛰️ Welcome to Coinspace!\nUse /help to see available commands.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Welcome message\n"
        "/help - Command list\n"
        "/analyze COIN - Full analysis\n"
        "/news COIN - News analysis only\n"
        "/tech COIN - Technical analysis only\n"
        "/signal COIN - Signal summary\n"
        "/satinal - VIP Satın Alma Bilgisi"
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
        "🎟 *Coinspace VIP Abonelik Planları:*\n"
        "• 1 Ay – 29.99$\n"
        "• 3 Ay – 69.99$\n"
        "• Ömür Boyu – 299.99$\n\n"
        "🪙 *Kabul edilen ödemeler:*\n"
        "USDT (TRC20), BTC, DOGE\n\n"
        "🔐 Satın aldıktan sonra otomatik VIP erişim sağlanır."
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

def start_bot():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("satinal", satinal))

    print("🚀 Coinspace Bot is running...")
    app.run_polling()