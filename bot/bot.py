import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
# Разные API ключи для разных моделей
DEEPSEEK_API_KEY = "sk-4d0fc9b811ed4d7b85e747b596ca8b65"
OPENAI_API_KEY = "sk-...your-openai-key..."
GEMINI_API_KEY = "your-gemini-key"

# Хранение текущей модели пользователя
user_models = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
Выбери модель:
/start_deepseek - DeepSeek
/start_openai - OpenAI
/start_gemini - Gemini
/ask [вопрос] - задать вопрос
""")

async def set_deepseek_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_models[update.effective_chat.id] = "deepseek"
    await update.message.reply_text("Теперь использую DeepSeek")

async def set_openai_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_models[update.effective_chat.id] = "openai"
    await update.message.reply_text("Теперь использую OpenAI")

async def set_gemini_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_models[update.effective_chat.id] = "gemini"
    await update.message.reply_text("Теперь использую Gemini")

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.replace('/ask ', '', 1)
    chat_id = update.effective_chat.id
    
    model = user_models.get(chat_id, "deepseek")
    
    try:
        if model == "deepseek":
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": user_message}], "stream": False}
            )
        elif model == "openai":
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": user_message}], "stream": False}
            )
        elif model == "gemini":
            # Для Gemini нужно использовать другую структуру
            pass
            
        data = response.json()
        bot_reply = data['choices'][0]['message']['content']
        await update.message.reply_text(bot_reply)

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("Произошла ошибка")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start_deepseek", set_deepseek_model))
    app.add_handler(CommandHandler("start_openai", set_openai_model))
    app.add_handler(CommandHandler("start_gemini", set_gemini_model))
    app.add_handler(CommandHandler("ask", ask_question))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question))

    app.run_polling()

if __name__ == '__main__':
    main()
