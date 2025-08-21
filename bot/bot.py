import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import httpx

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = "8320252272:AAGu8gHsoZHysN7jyCmMdEKjUtcwzXCgjTM"
OPENROUTER_API_KEY = "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"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот, который отвечает с помощью OpenRouter. Напиши мне что-нибудь!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": user_message}]
                }
            )

        if response.status_code != 200:
            await update.message.reply_text(f"Ошибка API OpenRouter: {response.status_code}")
            return

        data = response.json()
        bot_reply = data['choices'][0]['message']['content']
        await update.message.reply_text(bot_reply)

    except Exception as e:
        logger.error(f"Ошибка при обращении к OpenRouter: {e}")
        await update.message.reply_text("Извини, произошла ошибка.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен с OpenRouter...")
    app.run_polling()

if __name__ == '__main__':
    main()
