from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection

async def show_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает коллекцию героев пользователя"""
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception:
            pass  # Если callback уже просрочен, просто игнорируем
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        is_photo = query.message.photo
    else:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        is_photo = False

    collection = get_collection(user_id)

    if not collection:
        msg = "📭 *Коллекция пуста*\n\nОткрой свой первый пак — нажми кнопку «Открыть пак»!"
        keyboard = [[InlineKeyboardButton("🎁 Открыть пак", callback_data="free_pack")]]
        if query:
            if is_photo:
                try:
                    await query.message.delete()
                except Exception:
                    pass
                await context.bot.send_message(
                    chat_id=chat_id,
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
        else:
            await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Формируем текст коллекции
    text = "🌟 *Твоя коллекция героев:*\n\n"
    rarity_order = {"эпический": 0, "редкий": 1, "обычный": 2, "легендарный": -1}
    sorted_heroes = sorted(
        collection.values(),
        key=lambda h: (rarity_order.get(h.get("rarity", "обычный"), 3), h["name"])
    )

    for hero in sorted_heroes:
        emoji = {
            "эпический": "⭐",
            "редкий": "🔵",
            "обычный": "📘",
            "легендарный": "👑"
        }.get(hero.get("rarity", "обычный"), "📘")
        text += f"{emoji} *{hero['name']}* — {hero['book']} ({hero['rarity']})\n"

    if len(text) > 4000:
        text = text[:4000] + "\n\n...и ещё много героев!"

    keyboard = [[InlineKeyboardButton("🎁 Открыть пак", callback_data="free_pack")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        if is_photo:
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            try:
                await query.edit_message_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            except Exception:
                pass
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)