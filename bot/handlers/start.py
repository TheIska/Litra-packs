from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user, get_collection
from datetime import datetime, timedelta

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    collection = get_collection(user_id)

    # Таймер до следующего бесплатного пака
    last = user.get("last_free_pack")
    if last:
        last_time = datetime.fromisoformat(last)
        if datetime.now() - last_time < timedelta(hours=3):
            remaining = timedelta(hours=3) - (datetime.now() - last_time)
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            timer_text = f"⏳ Следующий бесплатный пак через {hours}ч {minutes}мин"
        else:
            timer_text = "✅ Бесплатный пак доступен!"
    else:
        timer_text = "✅ Бесплатный пак доступен!"

    keyboard = [
        [InlineKeyboardButton("🛒 Магазин паков", callback_data="shop")],
        [InlineKeyboardButton("📚 Моя коллекция", callback_data="collection")],
        [InlineKeyboardButton("⚔️ Дуэль", callback_data="duel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"📖 *Литературный Герой*\n\n"
        f"💰 Баланс: *{user['coins']}* монет\n"
        f"📚 Героев в коллекции: *{len(collection)}*\n"
        f"{timer_text}\n\n"
        "Используй кнопки ниже:"
    )

    if update.callback_query:
        query = update.callback_query
        await query.answer()
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
        chat_id = query.message.chat_id
        is_photo = query.message.photo
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
        if is_photo:
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
        await update.message.reply_text(help_text, parse_mode="Markdown")

async def show_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает баланс монет (вызывается по кнопке, но мы её убрали)"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    
    msg = f"💰 *Твой баланс:* {user['coins']} монет."
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
    """Магазин паков"""
    query = update.callback_query
    await query.answer()
    
    # Показываем баланс в магазине
    user_id = query.from_user.id
    user = get_user(user_id)
    
    keyboard = [
        [InlineKeyboardButton("📖 Дар читателя (бесплатно)", callback_data="free_pack")],
        [InlineKeyboardButton("📚 Маленький пак (200 монет)", callback_data="small_pack")],
        [InlineKeyboardButton("🔮 Лишний пак (500 монет)", callback_data="medium_pack")],
        [InlineKeyboardButton("✨ Новый пак (1000 монет)", callback_data="large_pack")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    
    msg = (
        f"🛒 *Магазин паков*\n\n"
        f"💰 Твой баланс: *{user['coins']}* монет\n\n"
        "Выбери, что хочешь открыть:"
    )
    
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