from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    
    keyboard = [
        [InlineKeyboardButton("📖 Дар читателя (бесплатно)", callback_data="free_pack")],
        [InlineKeyboardButton("📚 Карманный фолиант (200 монет)", callback_data="small_pack")],
        [InlineKeyboardButton("🔮 Тайная библиотека (500 монет)", callback_data="medium_pack")],
        [InlineKeyboardButton("✨ Редчайший манускрипт (1000 монет)", callback_data="large_pack")],
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
    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (без изменений)
    pass

async def show_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user(user_id)
    await query.edit_message_text(
        f"💰 *Твой баланс:* {user['coins']} монет.\n\n"
        "Зарабатывай монеты, участвуя в дуэлях (победа +10, поражение -5) и открывая паки!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]])
    )

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Магазин паков"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("📖 Дар читателя (бесплатно)", callback_data="free_pack")],
        [InlineKeyboardButton("📚 Маленький пак (200 монет)", callback_data="small_pack")],
        [InlineKeyboardButton("🔮 Лишний пак (500 монет)", callback_data="medium_pack")],
        [InlineKeyboardButton("✨ Новый пак (1000 монет)", callback_data="large_pack")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        "🛒 *Магазин паков*\n\n"
        "Выбери, что хочешь открыть:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )