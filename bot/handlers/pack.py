import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaAnimation
from telegram.ext import ContextTypes
from ..database import get_user, add_hero_to_collection, update_last_free_pack, get_collection, spend_coins
from ..models.hero import HEROES
from ..utils.image_generator import create_hero_card

RARITY_EMOJIS = {
    "обычный": "📘",
    "редкий": "🔵",
    "эпический": "🟣",
    "легендарный": "⭐",
}

PACK_NAMES = {
    "free": "📖 Дар читателя",
    "small": "📚 Маленький пак",
    "medium": "🔮 Лишний пак",
    "large": "✨ Новый пак"
}

PACK_RARITY_WEIGHTS = {
    "free": {"легендарный": 0.5, "эпический": 5.5, "редкий": 14, "обычный": 80},
    "small": {"легендарный": 2, "эпический": 8, "редкий": 30, "обычный": 60},
    "medium": {"легендарный": 5, "эпический": 15, "редкий": 50, "обычный": 30},
    "large": {"легендарный": 5, "эпический": 95, "редкий": 0, "обычный": 0}
}

PACK_PRICES = {
    "free": 0,
    "small": 200,
    "medium": 500,
    "large": 1000
}

FREE_PACK_INTERVAL = timedelta(hours=3)

# Анимированный GIF (можно заменить на свой)
GIF_URL = "https://media.tenor.com/2Lb0vKkL0bQAAAAi/sparkles.gif"

def get_hero_by_rarity_weights(weights):
    groups = {"легендарный": [], "эпический": [], "редкий": [], "обычный": []}
    for h in HEROES:
        groups[h.get("rarity", "обычный")].append(h)
    rarity_list = list(weights.keys())
    weight_values = list(weights.values())
    chosen_rarity = random.choices(rarity_list, weights=weight_values, k=1)[0]
    if not groups[chosen_rarity]:
        chosen_rarity = "обычный"
    return random.choice(groups[chosen_rarity])

async def open_pack(update: Update, context: ContextTypes.DEFAULT_TYPE, pack_type: str):
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
    else:
        user_id = update.effective_user.id

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
                msg = f"⏳ *Дар читателя* уже был открыт!\nСледующий через *{hours}ч {minutes}мин*."
                if query:
                    await query.edit_message_text(msg, parse_mode="Markdown")
                else:
                    await update.message.reply_text(msg, parse_mode="Markdown")
                return
    else:
        # Проверка монет
        price = PACK_PRICES[pack_type]
        if not spend_coins(user_id, price):
            msg = f"❌ Недостаточно монет! Нужно *{price}*.\nТвой баланс: *{user['coins']}*"
            if query:
                await query.edit_message_text(msg, parse_mode="Markdown")
            else:
                await update.message.reply_text(msg, parse_mode="Markdown")
            return

    # Выбор героя
    weights = PACK_RARITY_WEIGHTS[pack_type]
    hero = get_hero_by_rarity_weights(weights)
    add_hero_to_collection(user_id, hero)
    if pack_type == "free":
        update_last_free_pack(user_id, datetime.now())

    collection = get_collection(user_id)
    total = len(collection)

    # ========== АНИМАЦИЯ ==========
    # Отправляем GIF с анимацией
    if query:
        await query.edit_message_media(
            media=InputMediaAnimation(
                media=GIF_URL,
                caption=f"🎴 *Открываем {PACK_NAMES[pack_type]}...*",
                parse_mode="Markdown"
            )
        )
        await asyncio.sleep(1.5)  # Пауза для анимации
    else:
        await update.message.reply_animation(
            animation=GIF_URL,
            caption=f"🎴 *Открываем {PACK_NAMES[pack_type]}...*",
            parse_mode="Markdown"
        )
        await asyncio.sleep(1.5)

    # ========== КАРТОЧКА ==========
    image_bytes = create_hero_card(hero)
    emoji = RARITY_EMOJIS.get(hero.get("rarity", "обычный"), "📘")
    caption = (
        f"🎉 *Тебе выпал {hero['rarity']} герой!*\n\n"
        f"{emoji} *{hero['name']}*\n"
        f"📖 *{hero['book']}*\n"
        f"✍️ *{hero['author']}*\n\n"
        f"📊 В коллекции *{total}* героев."
    )
    if pack_type != "free":
        caption += f"\n💰 Осталось: *{user['coins'] - PACK_PRICES[pack_type]}* монет."

    keyboard = [
        [InlineKeyboardButton("📚 Моя коллекция", callback_data="collection")],
        [InlineKeyboardButton("🎁 Открыть другой пак", callback_data="shop")],
    ]

    if query:
        await query.edit_message_media(
            media=InputMediaPhoto(
                media=image_bytes,
                caption=caption,
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_photo(
            photo=image_bytes,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# Обработчики для разных паков
async def free_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_pack(update, context, "free")

async def small_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_pack(update, context, "small")

async def medium_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_pack(update, context, "medium")

async def large_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await open_pack(update, context, "large")