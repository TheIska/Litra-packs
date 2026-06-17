from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    keyboard = [
        [InlineKeyboardButton("📖 Дар читателя (бесплатно)", callback_data="free_pack")],
        [InlineKeyboardButton("📚 Маленький пак (200 монет)", callback_data="small_pack")],
        [InlineKeyboardButton("🔮 Лишний пак (500 монет)", callback_data="medium_pack")],
        [InlineKeyboardButton("✨ Новый пак (1000 монет)", callback_data="large_pack")],
        [InlineKeyboardButton("📚 Моя коллекция", callback_data="collection")],
        [InlineKeyboardButton("💰 Мои монеты", callback_data="coins")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"📖 *Литературный Герой*\n\n"
        f"Привет! У тебя *{user['coins']} монет*.\n"
        "Открывай паки, собирай героев и готовься к ЕГЭ!\n\n"
        "Выбери пак:"
    )
    
    # Проверяем, пришёл ли запрос как callback
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        # Если сообщение содержит картинку, отправляем новое вместо редактирования
        if query.message.photo:
            await query.message.delete()
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=welcome_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
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
    """Справка по боту"""
    query = update.callback_query
    if query:
        await query.answer()
        send_message = query.edit_message_text
        chat_id = query.message.chat_id
        message_id = query.message.message_id
        is_photo = query.message.photo
    else:
        send_message = update.message.reply_text
        chat_id = update.effective_chat.id
        message_id = None
        is_photo = False

    help_text = (
        "❓ *Как играть*\n\n"
        "1. Каждые 3 часа ты можешь открыть *бесплатный пак* (Дар читателя).\n"
        "2. За монеты можно купить улучшенные паки с большими шансами.\n"
        "3. Монеты зарабатываются в дуэлях (победа +10, поражение -5).\n"
        "4. Собирай коллекцию героев русской классики.\n"
        "5. Участвуй в дуэлях с друзьями и повышай рейтинг!\n\n"
        "📌 Бот создан для подготовки к ЕГЭ по литературе."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]]
    
    if query:
        if is_photo:
            # Если сообщение содержит картинку — отправляем новое
            await query.message.delete()
            await context.bot.send_message(
                chat_id=chat_id,
                text=help_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.edit_message_text(
                help_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    else:
        await send_message(help_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    
    msg = f"💰 *Твой баланс:* {user['coins']} монет.\n\nЗарабатывай монеты, участвуя в дуэлях (победа +10, поражение -5) и открывая паки!"
    keyboard = [[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]]
    
    if query.message.photo:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("📖 Дар читателя (бесплатно)", callback_data="free_pack")],
        [InlineKeyboardButton("📚 Маленький пак (200 монет)", callback_data="small_pack")],
        [InlineKeyboardButton("🔮 Лишний пак (500 монет)", callback_data="medium_pack")],
        [InlineKeyboardButton("✨ Новый пак (1000 монет)", callback_data="large_pack")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    
    msg = "🛒 *Магазин паков*\n\nВыбери, что хочешь открыть:"
    
    if query.message.photo:
        await query.message.delete()
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.edit_message_text(
            msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )