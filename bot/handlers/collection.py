from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection

async def show_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except:
            pass
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        # Удаляем старое сообщение, чтобы избежать редактирования
        try:
            await query.message.delete()
        except:
            pass
    else:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

    collection = get_collection(user_id)

    if not collection:
        text = "📭 *Коллекция пуста*\n\nОткрой свой первый пак!"
        keyboard = [[InlineKeyboardButton("🎁 Открыть пак", callback_data="free_pack")]]
    else:
        text = "🌟 *Твоя коллекция героев:*\n\n"
        rarity_order = {"легендарный": 0, "эпический": 1, "редкий": 2, "обычный": 3}
        sorted_heroes = sorted(
            collection.values(),
            key=lambda h: (rarity_order.get(h.get("rarity", "обычный"), 4), h["name"])
        )
        for hero in sorted_heroes:
            emoji = {
                "легендарный": "👑",
                "эпический": "⭐",
                "редкий": "🔵",
                "обычный": "📘"
            }.get(hero.get("rarity", "обычный"), "📘")
            text += f"{emoji} *{hero['name']}* — {hero['book']} ({hero['rarity']})\n"
        if len(text) > 4000:
            text = text[:4000] + "\n\n...и ещё много героев!"
        keyboard = [[InlineKeyboardButton("🎁 Открыть пак", callback_data="free_pack")]]

    # Отправляем новое сообщение
    if query:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )