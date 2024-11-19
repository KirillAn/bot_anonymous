import os
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

# Загрузка переменных из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен и Chat ID из переменных окружения
if os.path.exists('.env'):
    load_dotenv()
    print("Файл .env загружен.")
else:
    print("Файл .env не найден, загрузка переменных из системных переменных.")

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

if not TOKEN:
    print("Переменная BOT_TOKEN не установлена.")
    exit(1)
else:
    print("Переменная BOT_TOKEN загружена.")

if not ADMIN_CHAT_ID:
    print("Переменная ADMIN_CHAT_ID не установлена.")
    exit(1)
else:
    print("Переменная ADMIN_CHAT_ID загружена.")
CHOOSING, TYPING_STORY = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [['Поделиться историей']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        'Привет! Выберите действие:',
        reply_markup=markup
    )
    return CHOOSING

async def choose_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text == 'Поделиться историей':
        await update.message.reply_text(
            'Пожалуйста, отправьте вашу историю.',
            reply_markup=ReplyKeyboardRemove()
        )
        return TYPING_STORY
    else:
        await update.message.reply_text('Пожалуйста, выберите действующий пункт меню.')
        return CHOOSING

async def receive_story(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    story = update.message.text
    username = update.message.from_user.username or 'Аноним'
    # Отправляем историю админу
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f'Новая история от пользователя @{username}:\n\n{story}'
    )
    reply_keyboard = [['Поделиться историей']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        'Спасибо! Ваша история отправлена.',
        reply_markup=markup
    )
    return CHOOSING

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Действие отменено.', reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Text('Поделиться историей'), choose_action)
            ],
            TYPING_STORY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_story)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    logger.info('Бот запущен')
    application.run_polling()

if __name__ == '__main__':
    main()
