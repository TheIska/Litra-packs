 from telegram import Update
from telegram.ext import ContextTypes
from ..database import get_collection

async def show_collection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /collection и callback 'collection'.
    Показывает список всех героев в коллекции пользователя.
    """
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
        send_message = query.edit_message_text
    else:
        user_id = update.effective_user.id
        send_message = update.message.reply_text

    collection = get_collection(user_id)

    if not collection:
        await send_message(
            "📭 *Коллекция пуста*\n\n"
            "Открой свой первый пак — нажми кнопку «Открыть пак»!",
            parse_mode="Markdown"
        )
        return

    # Формируем текст
    text = "🌟 *Твоя коллекция героев:*\n\n"
    # Сортируем по редкости (эпические → редкие → обычные)
    rarity_order = {"эпический": 0, "редкий": 1, "обычный": 2}
    sorted_heroes = sorted(
        collection.values(),
        key=lambda h: (rarity_order.get(h.get("rarity", "обычный"), 3), h["name"])
    )

    for hero in sorted_heroes:
        emoji = {
            "эпический": "⭐",
            "редкий": "🔵",
            "обычный": "📘"
        }.get(hero.get("rarity", "обычный"), "📘")
        text += f"{emoji} *{hero['name']}* — {hero['book']} ({hero['rarity']})\n"

    # Ограничим длину, если слишком много героев
    if len(text) > 4000:
        text = text[:4000] + "\n\n...и ещё много героев!"

    # Кнопка "Назад" или "Открыть пак"
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [[InlineKeyboardButton("🎁 Открыть пак", callback_data="free_pack")]]
    await send_message(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )