from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection_sorted, get_collection_count, get_card_by_number
from ..models.hero import get_total_heroes
from ..utils.image_generator import create_hero_card
import logging

logger = logging.getLogger(__name__)

CARDS_PER_PAGE = 8

async def show_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает альбом с картами"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    page = context.user_data.get('album_page', 0)
    
    total = get_collection_count(user_id)
    total_heroes = get_total_heroes()
    
    if total == 0:
        keyboard = [[InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]]
        await query.edit_message_text(
            "📭 **Ваш альбом пуст!**\n\n"
            f"Всего в игре {total_heroes} героев.\n"
            "Откройте паки, чтобы начать собирать коллекцию.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return
    
    cards = get_collection_sorted(user_id, CARDS_PER_PAGE, page * CARDS_PER_PAGE)
    total_pages = (total - 1) // CARDS_PER_PAGE + 1
    
    text = f"📚 **Ваш альбом** (стр. {page + 1}/{total_pages})\n"
    text += f"📊 Собрано: {total}/{total_heroes} героев\n\n"
    
    # Группировка по авторам
    grouped = {}
    for card in cards:
        author = card.get('author', 'Неизвестный')
        if author not in grouped:
            grouped[author] = []
        grouped[author].append(card)
    
    for author, heroes in grouped.items():
        text += f"**{author}**\n"
        for hero in heroes:
            number = hero.get('card_number', 0)
            rarity_emoji = {
                "легендарный": "👑",
                "эпический": "💜",
                "редкий": "💎",
                "обычный": "📜"
            }.get(hero.get('rarity', 'обычный'), "📜")
            text += f"  {number:03d}. {rarity_emoji} {hero.get('name')}\n"
        text += "\n"
    
    keyboard = []
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
        
        card = get_card_by_number(user_id, number)
        if card:
            image_bytes = create_hero_card(card)
            await update.message.reply_photo(
                photo=image_bytes,
                caption=f"📖 **{card.get('name')}**\n"
                       f"🆔 № {number:03d}\n"
                       f"✍️ {card.get('author')}\n"
                       f"📚 {card.get('book')}\n"
                       f"⭐ {card.get('rarity', 'обычный').upper()}",
                parse_mode="Markdown"
            )
        else:
            # Показываем информацию о герое, даже если он не в коллекции
            from ..models.hero import get_hero_by_number
            hero_info = get_hero_by_number(number)
            if hero_info:
                await update.message.reply_text(
                    f"❌ Карта №{number:03d} **{hero_info['name']}**\n"
                    f"✍️ {hero_info['author']}\n"
                    f"📚 {hero_info['book']}\n\n"
                    "Этого героя ещё нет в вашем альбоме!\n"
                    "Откройте паки, чтобы найти его.",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(f"❌ Герой с номером {number} не существует")
        
        context.user_data['waiting_for_card_number'] = False
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число")