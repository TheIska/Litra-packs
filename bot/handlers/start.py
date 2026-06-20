# bot/handlers/start.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user, get_collection
from datetime import datetime, timedelta

ADMIN_ID = 6082384471

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    collection = get_collection(user_id)

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
        [InlineKeyboardButton("📝 Викторина", callback_data="quiz")],
        [InlineKeyboardButton("🛒 Магазин паков", callback_data="shop")],
        [InlineKeyboardButton("📚 Мой альбом", callback_data="album")],
        [InlineKeyboardButton("⚔️ Дуэль", callback_data="duel")],
        [InlineKeyboardButton("📩 Сообщить об ошибке", callback_data="report_error")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"📖 **Литературный Герой**\n\n"
        f"💰 Баланс: {user['coins']} монет\n"
        f"📚 Героев в альбоме: {len(collection)}\n"
        f"{timer_text}\n\n"
        "Используй кнопки ниже:"
    )

    if update.callback_query:
        query = update.callback_query
        try:
            await query.answer()
        except Exception:
            pass
        if query.message.photo:
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=welcome_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            try:
                await query.edit_message_text(
                    welcome_text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            except Exception:
                pass
    else:
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


async def report_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    
    text = (
        "📩 **Сообщить об ошибке**\n\n"
        "Если ты нашёл ошибку в боте или хочешь предложить идею, просто отправь сообщение с описанием проблемы.\n\n"
        "Спасибо за обратную связь!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user = update.effective_user
        user_name = user.first_name or "Пользователь"
        user_id = user.id
        
        message_text = (
            f"📩 Новое сообщение от пользователя\n\n"
            f"👤 Имя: {user_name}\n"
            f"🆔 ID: {user_id}\n\n"
            f"📝 Сообщение:\n{update.message.text}"
        )
        
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=message_text,
                parse_mode=None
            )
            await update.message.reply_text(
                "✅ Сообщение отправлено разработчику! Спасибо за обратную связь."
            )
        except Exception as e:
            print(f"❌ Ошибка отправки админу: {e}")
            await update.message.reply_text(
                "❌ Не удалось отправить сообщение. Попробуй позже."
            )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception:
            pass
        chat_id = query.message.chat_id
        is_photo = query.message.photo
    else:
        chat_id = update.effective_chat.id
        is_photo = False

    help_text = (
        "❓ **Список команд**\n\n"
        "/start — Главное меню\n"
        "/help — Эта справка\n"
        "/duel — Начать дуэль\n"
        "/stopduel — Завершить дуэль\n"
        "/quiz — Викторина\n"
        "/stopquiz — Завершить викторину\n"
        "/addcoins — (админ) Добавить монеты\n\n"
        "📌 **Как играть**\n"
        "1. Бесплатный пак каждые 3 часа.\n"
        "2. Покупай паки за монеты с лучшими шансами.\n"
        "3. Участвуй в дуэлях и зарабатывай монеты.\n"
        "4. Собирай альбом и готовься к ЕГЭ!\n"
        "5. Проходи викторину и получай бонусы!"
    )

    keyboard = [[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]]
    
    if query:
        if is_photo:
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(
                chat_id=chat_id,
                text=help_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            try:
                await query.edit_message_text(
                    help_text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                pass
    else:
        await update.message.reply_text(
            help_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def show_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    user_id = query.from_user.id
    user = get_user(user_id)
    
    msg = f"💰 **Твой баланс:** {user['coins']} монет.\n\nЗарабатывай монеты, участвуя в дуэлях (победа +10, поражение -5) и открывая паки!"
    keyboard = [[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]]
    
    if query.message.photo:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        try:
            await query.edit_message_text(
                msg,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    
    user_id = query.from_user.id
    user = get_user(user_id)
    
    keyboard = [
        [InlineKeyboardButton("📖 Дар читателя (бесплатно)", callback_data="free_pack")],
        [InlineKeyboardButton("📚 Маленький пак (200 монет)", callback_data="small_pack")],
        [InlineKeyboardButton("🔮 Лишний пак (500 монет)", callback_data="medium_pack")],
        [InlineKeyboardButton("✨ Новый пак (1000 монет)", callback_data="large_pack")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    
    msg = f"🛒 **Магазин паков**\n\n💰 Твой баланс: {user['coins']} монет\n\nВыбери, что хочешь открыть:"
    
    if query.message.photo:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        try:
            await query.edit_message_text(
                msg,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass