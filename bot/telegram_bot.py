from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, ContextTypes
from analysis.signal_generator import generate_signal
from analysis.news_analyzer import analyze_news
from analysis.technical_analyzer import get_technical_analysis
from utils.helpers import format_signal_result

def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CommandHandler("tech", tech))
    app.add_handler(CommandHandler("signal", signal))
    app.add_handler(CommandHandler("satinal", satinal))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛰️ Coinspace Bot'a Hoş Geldin!\nKomutlar için /help yazabilirsin.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Karşılama mesajı\n"
        "/help - Komut listesi\n"
        "/analyze COIN - Tam analiz\n"
        "/news COIN - Sadece haber analizi\n"
        "/tech COIN - Teknik analiz\n"
        "/signal COIN - Sinyal özeti\n"
        "/satinal - VIP planlar"
    )

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Lütfen coin sembolü girin. Örnek: /analyze BTCUSDT")
        return
    result = generate_signal(coin)
    msg = format_signal_result(result)
    await update.message.reply_text(msg)

async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Örnek kullanım: /news BTCUSDT")
        return
    result = analyze_news(coin)
    msg = f"🧠 Haber Duyarlılığı: {result['sentiment']}\n\n" + "\n".join([f"- {h}" for h in result['headlines']])
    await update.message.reply_text(msg)

async def tech(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Örnek kullanım: /tech BTCUSDT")
        return
    result = get_technical_analysis(coin)
    msg = f"📊 RSI: {result['rsi']}\n📈 Sinyal: {result['signal']}"
    await update.message.reply_text(msg)

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0].upper() if context.args else None
    if not coin:
        await update.message.reply_text("⚠️ Örnek kullanım: /signal BTCUSDT")
        return
    result = generate_signal(coin)
    await update.message.reply_text(f"✅ Final Sinyal: {result['final_signal']}")

async def satinal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("💳 VIP Satın Al", url="https://your-payment-link.com")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "🎟 *Coinspace VIP Abonelik Planları:*\n\n"
        "• 1 Ay – 149₺\n"
        "• 3 Ay – 399₺\n"
        "• Ömür Boyu – 999₺\n\n"
        "🪙 *Kabul edilen ödemeler:* USDT (TRC20), BTC, DOGE\n\n"
        "🔐 Satın aldıktan sonra otomatik VIP erişim sağlanır."
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)
