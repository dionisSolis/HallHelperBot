from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from config import TOKEN

STEPS = {
    "Концерт 🎤": [
        "1. Подключите микрофоны к микшеру.",
        "2. Настройте эквалайзер: усилите низкие частоты (бас) и средние частоты (голос).",
        "3. Проверьте громкость колонок.",
        "4. Включите сценическое освещение.",
    ],
    "Постановка 🎭": [
        "1. Закрепите петличные микрофоны на актёрах.",
        "2. Настройте эквалайзер: акцент на средние частоты (голос).",
        "3. Проверьте громкость колонок.",
        "4. Настройте прожекторы и цветные фильтры.",
    ],
    "Конференция 🎙️": [
        "1. Установите настольные микрофоны перед докладчиками.",
        "2. Настройте эквалайзер: акцент на высокие частоты (чёткость речи).",
        "3. Проверьте громкость колонок.",
        "4. Подключите проектор к ноутбуку.",
    ],
}

async def start(update: Update, context: CallbackContext):
    # Создаем клавиатуру с кнопками
    keyboard = [["Концерт 🎤", "Постановка 🎭"], ["Конференция 🎙️"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Выберите тип мероприятия:",
        reply_markup=reply_markup,
    )

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id

    if text in STEPS:
        context.user_data[user_id] = {
            "event_type": text,
            "current_step": 0,
        }
        await send_step(update, context, user_id)

    elif text == "✅ Готово":
        user_data = context.user_data.get(user_id)
        if user_data:
            current_step = user_data["current_step"]
            event_type = user_data["event_type"]
            steps = STEPS[event_type]

            if current_step < len(steps) - 1:
                user_data["current_step"] += 1
                await send_step(update, context, user_id)
            else:
                await update.message.reply_text("Все шаги выполнены! Мероприятие готово к запуску.")
                await start(update, context)

    elif text == "Вернуться в меню 🏠":
        await start(update, context)

async def send_step(update: Update, context: CallbackContext, user_id: int):
    user_data = context.user_data.get(user_id)
    if user_data:
        event_type = user_data["event_type"]
        current_step = user_data["current_step"]
        steps = STEPS[event_type]

        await update.message.reply_text(steps[current_step])

        keyboard = [["✅ Готово", "Вернуться в меню 🏠"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Нажмите '✅ Готово', чтобы перейти к следующему шагу, или 'Вернуться в меню 🏠', чтобы выйти.",
            reply_markup=reply_markup,
        )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()