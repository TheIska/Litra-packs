from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start.
    Показывает приветственное сообщение и главное меню с кнопками.
    """
    keyboard = [
        [InlineKeyboardButton("🎁 Открыть пак", callback_data="free_pack")],
        [InlineKeyboardButton("📚 Моя коллекция", callback_data="collection")],
        [InlineKeyboardButton("⚔️ Битва знаний", callback_data="duel")],
        [InlineKeyboardButton("❓ Как играть", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        "📖 *Литературный Герой*\n\n"
        "Открывай паки с героями русской классики, собирай коллекцию и готовься к ЕГЭ!\n"
        "Каждые 24 часа — бесплатный пак.\n\n"
        "Используй кнопки ниже, чтобы начать 👇"
    )

    # Если команда пришла через callback (например, после нажатия кнопки "Назад")
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /help и callback 'help'.
    Выводит справку по игре.
    """
    # Проверяем, пришёл ли запрос как callback
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        send_message = query.edit_message_text
    else:
        send_message = update.message.reply_text

    help_text = (
        "❓ *Как играть*\n\n"
        "1. Каждые 24 часа ты можешь открыть *бесплатный пак*.\n"
        "2. В паке тебе выпадает случайный герой из русской классики.\n"
        "3. Чем реже герой встречается — тем он ценнее (эпический > редкий > обычный).\n"
        "4. Собирай коллекцию и участвуй в дуэлях с друзьями!\n\n"
        "⚔️ *Дуэль*: выбери 3 героев для бонусов и отвечай на вопросы — побеждает тот, кто наберёт больше очков.\n\n"
        "📌 Бот создан для подготовки к ЕГЭ по литературе."
    )

    keyboard = [[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]]
    await send_message(
        help_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )