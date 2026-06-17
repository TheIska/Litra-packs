import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user, add_hero_to_collection, update_last_free_pack
from ..models.hero import HEROES

# Эмодзи для редкостей
RARITY_EMOJIS = {
    "обычный": "📘",
    "редкий": "🔵",
    "эпический": "🟣",
    "легендарный": "⭐",
}

async def free_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик открытия бесплатного пака (callback 'free_pack' или команда /free_pack).
    Проверяет, прошло ли 24 часа с последнего открытия, выдаёт случайного героя.
    """
    # Определяем, откуда пришёл запрос (callback или команда)
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
        send_message = query.edit_message_text
    else:
        user_id = update.effective_user.id
        send_message = update.message.reply_text

    user = get_user(user_id)

    # Проверка 24-часового лимита
    last = user.get("last_free_pack")
    if last:
        last_time = datetime.fromisoformat(last)
        if datetime.now() - last_time < timedelta(hours=24):
            remaining = timedelta(hours=24) - (datetime.now() - last_time)
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            await send_message(
                f"⏳ *Ты уже открывал бесплатный пак сегодня!*\n"
                f"Следующий будет доступен через *{hours}ч {minutes}мин*.\n\n"
                "Попробуй завтра!",
                parse_mode="Markdown"
            )
            return

    # Выбор случайного героя (можно добавить взвешенную редкость, но пока равномерно)
    hero = random.choice(HEROES)
    hero_key = f"{hero['author']} – {hero['name']}"

    # Сохраняем в коллекцию
    add_hero_to_collection(user_id, hero)
    update_last_free_pack(user_id, datetime.now())

    # Получаем обновлённый размер коллекции
    from ..database import get_collection
    collection = get_collection(user_id)
    total = len(collection)

    # Эмодзи редкости
    emoji = RARITY_EMOJIS.get(hero.get("rarity", "обычный"), "📘")

    # Формируем сообщение
    message = (
        f"🎉 *Тебе выпал {hero['rarity']} герой!*\n\n"
        f"{emoji} *{hero['name']}*\n"
        f"📖 *{hero['book']}*\n"
        f"✍️ *{hero['author']}*\n\n"
        f"📊 В твоей коллекции *{total}* героев."
    )

    # Кнопки для продолжения
    keyboard = [
        [InlineKeyboardButton("📚 Моя коллекция", callback_data="collection")],
        [InlineKeyboardButton("🎁 Открыть ещё (платно, в разработке)", callback_data="paid_pack")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await send_message(
            message,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )