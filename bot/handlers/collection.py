# bot/handlers/collection.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection_sorted, get_collection_count, get_card_by_number
from ..utils.image_generator import create_hero_card
import logging

logger = logging.getLogger(__name__)

CARDS_PER_PAGE = 6

async def show_collection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показывает альбом с картами"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Получаем параметры страницы
    page = context.user_data.get('album_page', 0)
    
    total = get_collection_count(user_id)
    if total == 0:
        keyboard = [[InlineKeyboardButton("🏠 В меню", callback_data="main_menu")]]
        await query.edit_message_text(
            "📭 У вас пока нет карт в коллекции!\n\n"
            "Откройте паки, чтобы начать собирать коллекцию.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # Получаем карты для текущей страницы
    offset = page * CARDS_PER_PAGE
    cards = get_collection_sorted(user_id, CARDS_PER_PAGE, offset)
    
    # Создаём сообщение
    total_pages = (total - 1) // CARDS_PER_PAGE + 1
    text = f"📚 **Ваш альбом** (стр. {page + 1}/{total_pages})\n"
    text += f"📊 Всего карт: {total}/225\n\n"
    
    # Добавляем карты в текст
    for i, card in enumerate(cards, 1):
        number = card.get('card_number', offset + i)
        rarity_emoji = {
            "легендарный": "👑",
            "эпический": "💜",
            "редкий": "💎",
            "обычный": "📜"
        }.get(card.get('rarity', 'обычный'), "📜")
        
        text += f"{number:03d}. {rarity_emoji} {card.get('name', 'Неизвестный')}\n"
    
    # Клавиатура
    keyboard = []
    
    # Кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data="album_prev"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data="album_next"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Кнопки для быстрого перехода по номерам
    number_buttons = []
    for i in range(1, 10):
        num = i * 25
        if num <= 225:
            number_buttons.append(InlineKeyboardButton(str(num), callback_data=f"album_goto_{num}"))
    keyboard.append(number_buttons)
    
    # Кнопка поиска по номеру
    keyboard.append([InlineKeyboardButton("🔍 Найти карту по номеру", callback_data="album_find")])
    
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
    
    await show_collection(update, context)


async def find_card_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Находит и показывает карту по номеру"""
    query = update.callback_query
    await query.answer()
    
    # Просим пользователя ввести номер
    keyboard = [[InlineKeyboardButton("❌ Отмена", callback_data="main_menu")]]
    await query.edit_message_text(
        "🔍 **Введите номер карты** (от 1 до 225)\n\n"
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
        if number < 1 or number > 225:
            await update.message.reply_text("❌ Номер должен быть от 1 до 225")
            return
        
        card = get_card_by_number(user_id, number)
        if card:
            # Отправляем карточку
            image_bytes = create_hero_card(card)
            await update.message.reply_photo(
                photo=image_bytes,
                caption=f"📖 **{card.get('name', 'Неизвестный')}**\n"
                       f"№ {number:03d}\n"
                       f"✍️ {card.get('author', 'Неизвестный')}\n"
                       f"📚 {card.get('work', 'Неизвестное произведение')}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❌ Карта №{number} не найдена в вашей коллекции")
        
        context.user_data['waiting_for_card_number'] = False
        
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите число")