from telegram.ext import CommandHandler

def setup_handlers(app):
    async def start(update, context):
        await update.message.reply_text("👋 Coinspace'e hoş geldin!")

    app.add_handler(CommandHandler("start", start))
