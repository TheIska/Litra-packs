from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection_count, get_card_by_number
from ..models.hero import HEROES_BY_NUMBER, get_total_heroes, get_hero_by_number, get_heroes_grouped
from ..utils.image_generator import create_hero_card
import logging

logger = logging.getLogger(__name__)

CARDS_PER_PAGE = 10  # Показываем по 10 героев на странице

async def show_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает альбом со всеми героями"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    page = context.user_data.get('album_page', 0)
    
    total_heroes = get_total_heroes()
    total_pages = (total_heroes - 1) // CARDS_PER_PAGE + 1
    
    # Получаем коллекцию пользователя
    from ..database import get_collection
    collection = get_collection(user_id)
    collected_numbers = set()
    for hero in collection.values():
        if hero.get('card_number', 0) > 0:
            collected_numbers.add(hero.get('card_number', 0))
    
    # Получаем всех героев для текущей страницы
    start_idx = page * CARDS_PER_PAGE
    end_idx = min(start_idx + CARDS_PER_PAGE, total_heroes)
    
    # Сортируем героев по номеру
    sorted_heroes = sorted(HEROES_BY_NUMBER.items())
    
    text = f"📚 **Ваш альбом** (стр. {page + 1}/{total_pages})\n"
    text += f"📊 Собрано: {len(collected_numbers)}/{total_heroes} героев\n\n"
    
    # Показываем героев на странице
    for i in range(start_idx, end_idx):
        if i < len(sorted_heroes):
            number, hero = sorted_heroes[i]
            is_collected = number in collected_numbers
            
            # Эмодзи статуса
            status = "✅" if is_collected else "❌"
            
            # Эмодзи редкости
            rarity_emoji = {
                "легендарный": "👑",
                "эпический": "💜",
                "редкий": "💎",
                "обычный": "📜"
            }.get(hero.get('rarity', 'обычный'), "📜")
            
            # Имя героя (обрезаем если длинное)
            name = hero.get('name', 'Неизвестный')
            if len(name) > 20:
                name = name[:18] + ".."
            
            text += f"{status} {number:03d}. {rarity_emoji} {name}\n"
            text += f"     ✍️ {hero.get('author', '')}\n"
            text += f"     📖 {hero.get('book', '')}\n\n"
    
    # Клавиатура
    keyboard = []
    
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
    
    # Кнопка поиска и главное меню
    keyboard.append([InlineKeyboardButton("🔍 Найти карту", callback_data="album_find")])
    keyboard.append([InlineKeyboardButton("🏠 В меню", callback_data="main_menu")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def album_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Навигация по альбому"""
    query = update.callback_query
    await query.answer()
    
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


async def find_card_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Находит и показывает карту по номеру"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="main_menu")]]
    await query.edit_message_text(
        "🔍 **Введите номер карты** (от 1 до 229)\n\n"
        "Просто напишите число в чат.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    context.user_data['waiting_for_card_number'] = True


async def handle_card_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ввод номера карты"""
    if not context.user_data.get('waiting_for_card_number'):
        return
    
    user_id = update.effective_user.id
    try:
        number = int(update.message.text)
        total_heroes = get_total_heroes()
        if number < 1 or number > total_heroes:
            await update.message.reply_text(f"❌ Номер должен быть от 1 до {total_heroes}")
            return
        
        # Проверяем, есть ли карта в коллекции
        card = get_card_by_number(user_id, number)
        hero_info = get_hero_by_number(number)
        
        if hero_info:
            if card:
                # Карта есть - показываем
                image_bytes = create_hero_card(card)
                await update.message.reply_photo(
                    photo=image_bytes,
                    caption=f"✅ **{hero_info['name']}**\n"
                           f"🆔 № {number:03d}\n"
                           f"✍️ {hero_info['author']}\n"
                           f"📚 {hero_info['book']}\n"
                           f"⭐ {hero_info.get('rarity', 'обычный').upper()}\n\n"
                           "🎉 Эта карта есть в вашем альбоме!",
                    parse_mode="Markdown"
                )
            else:
                # Карты нет - показываем информацию
                rarity_emoji = {
                    "легендарный": "👑",
                    "эпический": "💜",
                    "редкий": "💎",
                    "обычный": "📜"
                }.get(hero_info.get('rarity', 'обычный'), "📜")
                
                await update.message.reply_text(
                    f"❌ **{hero_info['name']}**\n"
                    f"🆔 № {number:03d}\n"
                    f"{rarity_emoji} {hero_info.get('rarity', 'обычный').upper()}\n"
                    f"✍️ {hero_info['author']}\n"
                    f"📚 {hero_info['book']}\n\n"
                    "😔 Этого героя ещё нет в вашем альбоме!\n"
                    "Откройте паки, чтобы найти его.",
                    parse_mode="Markdown"
                )
        else:
            await update.message.reply_text(f"❌ Герой с номером {number} не существует")
        
        context.user_data['waiting_for_card_number'] = False
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число")