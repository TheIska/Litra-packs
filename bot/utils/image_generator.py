import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user, add_hero_to_collection, update_last_free_pack, get_collection
from ..models.hero import HEROES
from ..utils.image_generator import create_hero_card

RARITY_EMOJIS = {
    "обычный": "📘",
    "редкий": "🔵",
    "эпический": "🟣",
    "легендарный": "⭐",
}

async def free_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
        send_message = query.edit_message_text
        send_photo = query.edit_message_media
    else:
        user_id = update.effective_user.id
        send_message = update.message.reply_text
        send_photo = update.message.reply_photo

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
                f"Следующий будет доступен через *{hours}ч {minutes}мин*.",
                parse_mode="Markdown"
            )
            return

    # Выбор случайного героя
    hero = random.choice(HEROES)
    hero_key = f"{hero['author']} – {hero['name']}"

    # Сохраняем в коллекцию
    add_hero_to_collection(user_id, hero)
    update_last_free_pack(user_id, datetime.now())

    collection = get_collection(user_id)
    total = len(collection)

    # Генерируем карточку
    image_bytes = create_hero_card(hero)

    # Формируем подпись
    emoji = RARITY_EMOJIS.get(hero.get("rarity", "обычный"), "📘")
    caption = (
        f"🎉 *Тебе выпал {hero['rarity']} герой!*\n\n"
        f"{emoji} *{hero['name']}*\n"
        f"📖 *{hero['book']}*\n"
        f"✍️ *{hero['author']}*\n\n"
        f"📊 В твоей коллекции *{total}* героев."
    )

    keyboard = [
        [InlineKeyboardButton("📚 Моя коллекция", callback_data="collection")],
        [InlineKeyboardButton("🎁 Открыть ещё", callback_data="free_pack")],
    ]

    # Отправляем карточку
    if query:
        await query.edit_message_media(
            media=InputMediaPhoto(media=image_bytes, caption=caption, parse_mode="Markdown"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await send_photo(
            photo=image_bytes,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )