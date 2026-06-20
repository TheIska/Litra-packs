from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user, get_collection
from datetime import datetime, timedelta

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
        [InlineKeyboardButton("📝 Ежедневная викторина", callback_data="quiz")],
        [InlineKeyboardButton("🛒 Магазин паков", callback_data="shop")],
        [InlineKeyboardButton("📚 Моя коллекция", callback_data="collection")],
        [InlineKeyboardButton("⚔️ Дуэль", callback_data="duel")],
        [InlineKeyboardButton("❓ Помощь / Команды", callback_data="help")],
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

# ... остальные функции (help_command, show_coins, shop) без изменений ...