from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

if not TOKEN or not ADMIN_CHAT_ID:
    logger.error("Переменные окружения BOT_TOKEN и ADMIN_CHAT_ID должны быть установлены")
    exit(1)



# Определяем состояния для ConversationHandler
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

    # Определяем ConversationHandler
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

    application.run_polling()

if __name__ == '__main__':
    main()
