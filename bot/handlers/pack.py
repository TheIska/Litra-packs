import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from ..database import get_user, add_hero_to_collection, update_last_free_pack, get_collection, spend_coins, add_coins
from ..models.hero import HEROES
from ..utils.image_generator import create_hero_card

RARITY_EMOJIS = {
    "обычный": "📘",
    "редкий": "🔵",
    "эпический": "🟣",
    "легендарный": "⭐",
}

# Названия паков
PACK_NAMES = {
    "free": "📖 Дар читателя",
    "small": "📚 Карманный фолиант",
    "medium": "🔮 Тайная библиотека",
    "large": "✨ Редчайший манускрипт"
}

# Шансы для каждого пака (в процентах)
PACK_RARITY_WEIGHTS = {
    "free": {"легендарный": 0.5, "эпический": 5.5, "редкий": 14, "обычный": 80},
    "small": {"легендарный": 2, "эпический": 8, "редкий": 30, "обычный": 60},
    "medium": {"легендарный": 5, "эпический": 15, "редкий": 50, "обычный": 30},
    "large": {"легендарный": 5, "эпический": 95, "редкий": 0, "обычный": 0}  # только легендарные и эпические
}

# Цены в монетах
PACK_PRICES = {
    "free": 0,
    "small": 200,
    "medium": 500,
    "large": 1000
}

# Таймер для бесплатного пака (3 часа)
FREE_PACK_INTERVAL = timedelta(hours=3)

GIF_URL = "https://media.tenor.com/2Lb0vKkL0bQAAAAi/sparkles.gif"

def get_hero_by_rarity_weights(weights):
    """Выбирает редкость по весам, затем случайного героя этой редкости."""
    # Группируем героев по редкости
    groups = {"легендарный": [], "эпический": [], "редкий": [], "обычный": []}
    for h in HEROES:
        groups[h.get("rarity", "обычный")].append(h)
    
    # Выбираем редкость
    rarity_list = list(weights.keys())
    weight_values = list(weights.values())
    chosen_rarity = random.choices(rarity_list, weights=weight_values, k=1)[0]
    
    # Если в группе нет героев (может быть, если не добавили легендарных), берём обычного
    if not groups[chosen_rarity]:
        chosen_rarity = "обычный"
    
    return random.choice(groups[chosen_rarity])

async def open_pack(update: Update, context: ContextTypes.DEFAULT_TYPE, pack_type: str):
    """Общая функция для открытия пака."""
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
        send_message = query.edit_message_text
        send_animation = query.edit_message_media
        send_photo = query.edit_message_media
    else:
        user_id = update.effective_user.id
        send_message = update.message.reply_text
        send_animation = update.message.reply_animation
        send_photo = update.message.reply_photo

    user = get_user(user_id)

    # Проверка для бесплатного пака
    if pack_type == "free":
        last = user.get("last_free_pack")
        if last:
            last_time = datetime.fromisoformat(last)
            if datetime.now() - last_time < FREE_PACK_INTERVAL:
                remaining = FREE_PACK_INTERVAL - (datetime.now() - last_time)
                hours = int(remaining.total_seconds() // 3600)
                minutes = int((remaining.total_seconds() % 3600) // 60)
                await send_message(
                    f"⏳ *Дар читателя* уже был открыт!\n"
                    f"Следующий будет доступен через *{hours}ч {minutes}мин*.",
                    parse_mode="Markdown"
                )
                return
    else:
        # Проверка монет для платных паков
        price = PACK_PRICES[pack_type]
        if not spend_coins(user_id, price):
            await send_message(
                f"❌ У тебя недостаточно монет! Нужно *{price} монет*.\n"
                f"Твой баланс: *{user['coins']}* монет.",
                parse_mode="Markdown"
            )
            return

    # Получаем героя по шансам
    weights = PACK_RARITY_WEIGHTS[pack_type]
    hero = get_hero_by_rarity_weights(weights)
    add_hero_to_collection(user_id, hero)
    if pack_type == "free":
        update_last_free_pack(user_id, datetime.now())

    collection = get_collection(user_id)
    total = len(collection)

    # Анимация (только для бесплатного пака? можно для всех)
    if query:
        await query.edit_message_media(
            media=InputMediaPhoto(media=GIF_URL, caption=f"🎴 *Открываем {PACK_NAMES[pack_type]}...*"),
            parse_mode="Markdown"
        )
        await asyncio.sleep(1.5)
    else:
        await send_animation(
            animation=GIF_URL,
            caption=f"🎴 *Открываем {PACK_NAMES[pack_type]}...*",
            parse_mode="Markdown"
        )
        await asyncio.sleep(1.5)

    # Генерируем карточку
    image_bytes = create_hero_card(hero)

    emoji = RARITY_EMOJIS.get(hero.get("rarity", "обычный"), "📘")
    caption = (
        f"🎉 *Тебе выпал {hero['rarity']} герой!*\n\n"
        f"{emoji} *{hero['name']}*\n"
        f"📖 *{hero['book']}*\n"
        f"✍️ *{hero['author']}*\n\n"
        f"📊 В твоей коллекции *{total}* героев."
    )
    if pack_type != "free":
        caption += f"\n💰 Осталось монет: *{user['coins'] - PACK_PRICES[pack_type]}*"

    keyboard = [
        [InlineKeyboardButton("📚 Моя коллекция", callback_data="collection")],
        [InlineKeyboardButton("🎁 Открыть другой пак", callback_data="shop")],
    ]
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

# Обработчики для каждого типа пака
async def free_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_pack(update, context, "free")

async def small_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_pack(update, context, "small")

async def medium_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_pack(update, context, "medium")

async def large_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_pack(update, context, "large")