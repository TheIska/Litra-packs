from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection_count, get_card_by_number, get_collection
from ..models.hero import HEROES_BY_NUMBER, get_total_heroes, get_hero_by_number
from ..utils.image_generator import create_hero_card
import logging

logger = logging.getLogger(__name__)

CARDS_PER_PAGE = 8

async def show_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает альбом со всеми героями"""
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception as e:
            print(f"Ошибка answer: {e}")
    
    user_id = update.effective_user.id
    page = context.user_data.get('album_page', 0)
    
    total_heroes = get_total_heroes()
    total_pages = (total_heroes - 1) // CARDS_PER_PAGE + 1
    
    # Получаем коллекцию пользователя
    collection = get_collection(user_id)
    collected_numbers = set()
    for hero in collection.values():
        if hero.get('card_number', 0) > 0:
            collected_numbers.add(hero.get('card_number', 0))
    
    # Получаем всех героев для текущей страницы
    start_idx = page * CARDS_PER_PAGE
    end_idx = min(start_idx + CARDS_PER_PAGE, total_heroes)
    sorted_heroes = sorted(HEROES_BY_NUMBER.items())
    
    text = f"📚 **Ваш альбом** (стр. {page + 1}/{total_pages})\n"
    text += f"📊 Собрано: {len(collected_numbers)}/{total_heroes} героев\n\n"
    
    keyboard = []
    
    for i in range(start_idx, end_idx):
        if i < len(sorted_heroes):
            number, hero = sorted_heroes[i]
            is_collected = number in collected_numbers
            
            status = "✅" if is_collected else "❌"
            
            rarity_emoji = {
                "легендарный": "👑",
                "эпический": "💜",
                "редкий": "💎",
                "обычный": "📜"
            }.get(hero.get('rarity', 'обычный'), "📜")
            
            name = hero.get('name', 'Неизвестный')
            if len(name) > 20:
                name = name[:18] + ".."
            
            button_text = f"{status} {number:03d}. {rarity_emoji} {name}"
            callback_data = f"album_card_{number}"
            keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data="album_prev"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data="album_next"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Быстрые переходы по номерам
    number_buttons = []
    for i in range(1, 10):
        num = i * 25
        if num <= total_heroes:
            number_buttons.append(InlineKeyboardButton(str(num), callback_data=f"album_goto_{num}"))
    keyboard.append(number_buttons)
    
    keyboard.append([InlineKeyboardButton("🏠 В меню", callback_data="main_menu")])
    
    try:
        if query and query.message:
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Ошибка при показе альбома: {e}")
        logger.error(f"Ошибка при показе альбома: {e}")


async def album_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Навигация по альбому"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        print(f"Ошибка answer в навигации: {e}")
    
    action = query.data
    
    if action == "album_prev":
        context.user_data['album_page'] = context.user_data.get('album_page', 0) - 1
    elif action == "album_next":
        context.user_data['album_page'] = context.user_data.get('album_page', 0) + 1
    elif action.startswith("album_goto_"):
        number = int(action.split("_")[2])
        page = (number - 1) // CARDS_PER_PAGE
        context.user_data['album_page'] = page
    
    await show_album(update, context)


async def show_card_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает карту по номеру (по нажатию на кнопку)"""
    query = update.callback_query
    
    # ОБЯЗАТЕЛЬНО отвечаем на callback
    try:
        await query.answer()
        print(f"✅ Ответили на callback")
    except Exception as e:
        print(f"❌ Ошибка при answer: {e}")
    
    user_id = update.effective_user.id
    chat_id = query.message.chat_id
    
    # Получаем номер карты
    try:
        number = int(query.data.split("_")[2])
        print(f"🔍 Номер карты: {number}")
    except Exception as e:
        print(f"❌ Ошибка при получении номера: {e}")
        await query.edit_message_text("❌ Ошибка! Попробуйте снова.")
        return
    
    # Проверяем, есть ли карта
    card = get_card_by_number(user_id, number)
    hero_info = get_hero_by_number(number)
    
    print(f"📊 Карта: {card}, Герой: {hero_info}")
    
    if not hero_info:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ Герой с номером {number} не существует"
        )
        return
    
    if card:
        try:
            print(f"🎴 Генерируем карточку для {hero_info['name']}")
            image_bytes = create_hero_card(card)
            
            await context.bot.send_photo(
                chat_id=chat_id,
                photo=image_bytes,
                caption=f"✅ **{hero_info['name']}**\n"
                       f"🆔 № {number:03d}\n"
                       f"✍️ {hero_info['author']}\n"
                       f"📚 {hero_info['book']}\n"
                       f"⭐ {hero_info.get('rarity', 'обычный').upper()}\n\n"
                       "🎉 Эта карта есть в вашем альбоме!",
                parse_mode="Markdown"
            )
            print(f"✅ Карточка отправлена!")
        except Exception as e:
            print(f"❌ Ошибка при создании карточки: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Ошибка при создании карточки. Попробуйте позже."
            )
    else:
        rarity_emoji = {
            "легендарный": "👑",
            "эпический": "💜",
            "редкий": "💎",
            "обычный": "📜"
        }.get(hero_info.get('rarity', 'обычный'), "📜")
        
        keyboard = [[InlineKeyboardButton("🔙 Назад в альбом", callback_data="album_back")]]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ **{hero_info['name']}**\n"
                 f"🆔 № {number:03d}\n"
                 f"{rarity_emoji} {hero_info.get('rarity', 'обычный').upper()}\n"
                 f"✍️ {hero_info['author']}\n"
                 f"📚 {hero_info['book']}\n\n"
                 "😔 Этого героя ещё нет в вашем альбоме!\n"
                 "Откройте паки, чтобы найти его.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


async def album_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Возврат в альбом"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        print(f"Ошибка answer в album_back: {e}")
    
    # Восстанавливаем страницу альбома
    await show_album(update, context)