from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection_with_duplicates, get_connection, add_coins, get_user
from ..models.hero import HEROES_BY_NUMBER, get_total_heroes
from ..utils.image_generator import create_hero_card
import logging
import traceback
import sqlite3
import asyncio

logger = logging.getLogger(__name__)

CARDS_PER_PAGE = 8
DUPLICATES_PER_PAGE = 5

DUPLICATE_PRICES = {
    "легендарный": 500,
    "эпический": 150,
    "редкий": 50,
    "обычный": 20,
}


async def show_album(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("🔵 show_album вызван")
        
        query = update.callback_query
        if query:
            try:
                await query.answer()
            except Exception as e:
                print(f"Ошибка answer в show_album: {e}")
        
        user_id = update.effective_user.id
        page = context.user_data.get('album_page', 0)
        
        total_heroes = get_total_heroes()
        total_pages = (total_heroes - 1) // CARDS_PER_PAGE + 1
        
        collection = get_collection_with_duplicates(user_id)
        print(f"📊 Коллекция пользователя {user_id}: {len(collection)} карт")
        
        collected_numbers = {}
        for hero in collection:
            number = hero.get('card_number', 0)
            if number > 0:
                collected_numbers[number] = hero.get('duplicates', 1)
        
        print(f"📊 Всего выбито: {len(collected_numbers)}/{total_heroes}")
        
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
                duplicates = collected_numbers.get(number, 0)
                
                if is_collected:
                    if duplicates > 1:
                        status = f"🔄 x{duplicates}"
                    else:
                        status = "✅"
                else:
                    status = "❌"
                
                rarity_emoji = {
                    "легендарный": "👑",
                    "эпический": "💜",
                    "редкий": "💎",
                    "обычный": "📜"
                }.get(hero.get('rarity', 'обычный'), "📜")
                
                name = hero.get('name', 'Неизвестный')
                if len(name) > 18:
                    name = name[:16] + ".."
                
                button_text = f"{status} {number:03d}. {rarity_emoji} {name}"
                callback_data = f"album_card_{number}"
                keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data="album_prev"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Вперед ▶️", callback_data="album_next"))
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        number_buttons = []
        for i in range(1, 10):
            num = i * 25
            if num <= total_heroes:
                number_buttons.append(InlineKeyboardButton(str(num), callback_data=f"album_goto_{num}"))
        keyboard.append(number_buttons)
        
        keyboard.append([InlineKeyboardButton("💰 Продать дубликаты", callback_data="sell_duplicates_menu|0")])
        keyboard.append([InlineKeyboardButton("🏠 В меню", callback_data="main_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if query and query.message:
            try:
                if query.message.text:
                    await query.edit_message_text(
                        text,
                        reply_markup=reply_markup,
                        parse_mode="Markdown"
                    )
                    print("✅ Альбом обновлён")
                else:
                    try:
                        await query.message.delete()
                    except:
                        pass
                    await context.bot.send_message(
                        chat_id=query.message.chat_id,
                        text=text,
                        reply_markup=reply_markup,
                        parse_mode="Markdown"
                    )
                    print("✅ Альбом отправлен новым сообщением")
            except Exception as e:
                print(f"❌ Ошибка при редактировании: {e}")
                try:
                    await query.message.delete()
                except:
                    pass
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
                print("✅ Альбом отправлен новым сообщением")
        else:
            await update.message.reply_text(
                text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            print("✅ Альбом отправлен")
            
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в show_album: {e}")
        traceback.print_exc()


async def album_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        query = update.callback_query
        action = query.data
        
        print(f"🟣 album_navigation вызван, действие: {action}")
        
        if action.startswith("album_card_"):
            print("🟣 Это карточка! Пропускаем для show_card_by_number")
            return
        
        await query.answer()
        
        if action == "album_prev":
            context.user_data['album_page'] = context.user_data.get('album_page', 0) - 1
        elif action == "album_next":
            context.user_data['album_page'] = context.user_data.get('album_page', 0) + 1
        elif action.startswith("album_goto_"):
            number = int(action.split("_")[2])
            page = (number - 1) // CARDS_PER_PAGE
            context.user_data['album_page'] = page
        else:
            return
        
        await show_album(update, context)
        
    except Exception as e:
        print(f"❌ Ошибка в album_navigation: {e}")
        traceback.print_exc()


async def sell_duplicates_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Меню продажи дубликатов"""
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception as e:
            print(f"❌ Ошибка при answer: {e}")
    
    user_id = update.effective_user.id
    chat_id = query.message.chat_id if query else update.effective_chat.id
    
    data = query.data if query else ""
    parts = data.split("|") if data else []
    
    page = int(parts[1]) if len(parts) > 1 else context.user_data.get('duplicates_page', 0)
    context.user_data['duplicates_page'] = page
    
    collection = get_collection_with_duplicates(user_id)
    cards_with_duplicates = []
    total_duplicates = 0
    total_coins = 0
    
    for hero in collection:
        duplicates = hero.get('duplicates', 1)
        if duplicates > 1:
            rarity = hero.get('rarity', 'обычный')
            price = DUPLICATE_PRICES.get(rarity, 20)
            sell_count = duplicates - 1
            cards_with_duplicates.append({
                'name': hero.get('name', 'Неизвестный'),
                'card_number': hero.get('card_number', 0),
                'duplicates': duplicates,
                'sell_count': sell_count,
                'rarity': rarity,
                'price': price,
                'total_price': sell_count * price,
                'hero_key': hero.get('hero_key', '')
            })
            total_duplicates += sell_count
            total_coins += sell_count * price
    
    rarity_order = {"легендарный": 0, "эпический": 1, "редкий": 2, "обычный": 3}
    cards_with_duplicates.sort(key=lambda x: rarity_order.get(x['rarity'], 4))
    
    if not cards_with_duplicates:
        text = "📭 У вас нет дубликатов для продажи!\n\nОткрывайте паки, чтобы получить дубликаты."
        keyboard = [[InlineKeyboardButton("🔙 Назад в альбом", callback_data="album_back")]]
        if query:
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    total_pages = (len(cards_with_duplicates) - 1) // DUPLICATES_PER_PAGE + 1
    start_idx = page * DUPLICATES_PER_PAGE
    end_idx = min(start_idx + DUPLICATES_PER_PAGE, len(cards_with_duplicates))
    page_cards = cards_with_duplicates[start_idx:end_idx]
    
    price_text = "💎 *Цены за дубликат:*\n"
    price_text += f"👑 Легендарный: {DUPLICATE_PRICES['легендарный']} монет\n"
    price_text += f"💜 Эпический: {DUPLICATE_PRICES['эпический']} монет\n"
    price_text += f"💎 Редкий: {DUPLICATE_PRICES['редкий']} монет\n"
    price_text += f"📜 Обычный: {DUPLICATE_PRICES['обычный']} монет\n\n"
    
    text = f"💰 *Продажа дубликатов*\n\n{price_text}"
    text += f"📊 Всего дубликатов: {total_duplicates}\n"
    text += f"💵 Общая сумма: {total_coins} монет\n\n"
    text += f"📄 Страница {page + 1}/{total_pages}\n"
    text += "Выберите карту для продажи дубликатов:\n\n"
    
    keyboard = []
    
    for card in page_cards:
        rarity_emoji = {
            "легендарный": "👑",
            "эпический": "💜",
            "редкий": "💎",
            "обычный": "📜"
        }.get(card['rarity'], "📜")
        
        button_text = (
            f"{rarity_emoji} {card['name']} "
            f"(x{card['duplicates']}) → {card['total_price']} монет"
        )
        keyboard.append([
            InlineKeyboardButton(
                button_text,
                callback_data=f"sell_duplicates_card|{card['card_number']}"
            )
        ])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"sell_duplicates_menu|{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"sell_duplicates_menu|{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    if total_duplicates > 0:
        keyboard.append([
            InlineKeyboardButton(
                f"🔥 Продать ВСЕ дубликаты ({total_duplicates} шт. за {total_coins} монет)",
                callback_data="sell_duplicates_all"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад в альбом", callback_data="album_back")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if query:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    except Exception as e:
        if "Message is not modified" in str(e):
            await query.answer("Уже на этой странице")
        else:
            raise e


async def sell_duplicates_card(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Продажа дубликатов конкретной карты с подтверждением"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        print(f"❌ Ошибка при answer: {e}")
    
    user_id = update.effective_user.id
    chat_id = query.message.chat_id
    
    parts = query.data.split("|")
    if len(parts) < 2:
        await query.edit_message_text("❌ Ошибка! Попробуйте снова.")
        return
    
    try:
        card_number = int(parts[1])
    except ValueError:
        await query.edit_message_text("❌ Ошибка! Попробуйте снова.")
        return
    
    collection = get_collection_with_duplicates(user_id)
    card = None
    for hero in collection:
        if hero.get('card_number', 0) == card_number:
            card = hero
            break
    
    if not card:
        await query.edit_message_text("❌ Карта не найдена!")
        return
    
    duplicates = card.get('duplicates', 1)
    if duplicates <= 1:
        await query.edit_message_text("❌ У этой карты нет дубликатов для продажи!")
        return
    
    rarity = card.get('rarity', 'обычный')
    price = DUPLICATE_PRICES.get(rarity, 20)
    sell_count = duplicates - 1
    total = sell_count * price
    
    text = (
        f"⚠️ *Подтверждение продажи*\n\n"
        f"🎴 Карта: *{card.get('name')}*\n"
        f"🆔 №{card_number:03d}\n"
        f"⭐ {rarity.upper()}\n"
        f"🔄 Дубликатов: {duplicates} шт.\n"
        f"💰 Продаётся: {sell_count} шт.\n"
        f"💵 Цена: {price} монет/шт\n"
        f"💎 Итого: *{total} монет*\n\n"
        f"✅ После продажи останется 1 карта (оригинал).\n"
        f"❓ Вы действительно хотите продать дубликаты этой карты?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, продать", callback_data=f"sell_duplicates_confirm|{card_number}"),
            InlineKeyboardButton("❌ Отмена", callback_data="sell_duplicates_menu|0")
        ]
    ]
    
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        if "Message is not modified" in str(e):
            await query.answer("Уже на этой странице")
        else:
            raise e


async def sell_duplicates_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Подтверждение продажи дубликатов"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        print(f"❌ Ошибка при answer: {e}")
    
    user_id = update.effective_user.id
    
    parts = query.data.split("|")
    if len(parts) < 2:
        await query.edit_message_text("❌ Ошибка! Попробуйте снова.")
        return
    
    try:
        card_number = int(parts[1])
    except ValueError:
        await query.edit_message_text("❌ Ошибка! Попробуйте снова.")
        return
    
    collection = get_collection_with_duplicates(user_id)
    card = None
    for hero in collection:
        if hero.get('card_number', 0) == card_number:
            card = hero
            break
    
    if not card:
        await query.edit_message_text("❌ Карта не найдена!")
        return
    
    duplicates = card.get('duplicates', 1)
    if duplicates <= 1:
        await query.edit_message_text("❌ У этой карты нет дубликатов для продажи!")
        return
    
    rarity = card.get('rarity', 'обычный')
    price = DUPLICATE_PRICES.get(rarity, 20)
    sell_count = duplicates - 1
    total = sell_count * price
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = get_connection()
            c = conn.cursor()
            
            c.execute(
                "UPDATE collection SET duplicates = 1 WHERE user_id = ? AND card_number = ?",
                (user_id, card_number)
            )
            conn.commit()
            conn.close()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            raise e
    
    add_coins(user_id, total)
    
    user = get_user(user_id)
    
    text = (
        f"✅ *Продажа выполнена!*\n\n"
        f"🎴 {card.get('name')}\n"
        f"🔄 Продано: {sell_count} дубликатов\n"
        f"💵 Получено: *{total} монет*\n"
        f"💰 Новый баланс: *{user['coins']} монет*\n\n"
        f"📦 Осталось: 1 карта (оригинал)"
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Назад к дубликатам", callback_data="sell_duplicates_menu|0")]]
    
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        if "Message is not modified" in str(e):
            await query.answer("Уже на этой странице")
        else:
            raise e


async def sell_duplicates_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Подтверждение продажи всех дубликатов"""
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        print(f"❌ Ошибка при answer: {e}")
    
    user_id = update.effective_user.id
    
    collection = get_collection_with_duplicates(user_id)
    total_duplicates = 0
    total_coins = 0
    cards_list = []
    
    for hero in collection:
        duplicates = hero.get('duplicates', 1)
        if duplicates > 1:
            rarity = hero.get('rarity', 'обычный')
            price = DUPLICATE_PRICES.get(rarity, 20)
            sell_count = duplicates - 1
            total_duplicates += sell_count
            total_coins += sell_count * price
            cards_list.append(f"{hero.get('name')} (x{duplicates})")
    
    if total_duplicates == 0:
        await query.edit_message_text("❌ Нет дубликатов для продажи!")
        return
    
    text = (
        f"⚠️ *Подтверждение массовой продажи*\n\n"
        f"🔥 Вы собираетесь продать ВСЕ дубликаты!\n\n"
        f"📋 Будут проданы дубликаты следующих карт:\n"
        f"{chr(10).join(['• ' + card for card in cards_list[:10]])}"
        f"{chr(10) + '• ...и ещё ' + str(len(cards_list) - 10) if len(cards_list) > 10 else ''}\n\n"
        f"🔄 Всего дубликатов: {total_duplicates}\n"
        f"💵 Общая сумма: *{total_coins} монет*\n\n"
        f"✅ После продажи у всех карт останется по 1 экземпляру.\n"
        f"❓ Вы действительно хотите продать все дубликаты?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, продать всё", callback_data="sell_duplicates_all_confirm"),
            InlineKeyboardButton("❌ Отмена", callback_data="sell_duplicates_menu|0")
        ]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")


async def sell_duplicates_all_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Подтверждение продажи всех дубликатов"""
    query = update.callback_query
    # НЕ ДЕЛАЕМ await query.answer() ЗДЕСЬ, ЧТОБЫ НЕ БЛОКИРОВАТЬ
    
    user_id = update.effective_user.id
    
    collection = get_collection_with_duplicates(user_id)
    total_duplicates = 0
    total_coins = 0
    sold_cards = []
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = get_connection()
            c = conn.cursor()
            
            for hero in collection:
                duplicates = hero.get('duplicates', 1)
                if duplicates > 1:
                    rarity = hero.get('rarity', 'обычный')
                    price = DUPLICATE_PRICES.get(rarity, 20)
                    sell_count = duplicates - 1
                    total_duplicates += sell_count
                    total_coins += sell_count * price
                    sold_cards.append(f"{hero.get('name')} (x{duplicates} → 1)")
                    
                    c.execute(
                        "UPDATE collection SET duplicates = 1 WHERE user_id = ? AND card_number = ?",
                        (user_id, hero.get('card_number', 0))
                    )
            
            conn.commit()
            conn.close()
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            raise e
    
    add_coins(user_id, total_coins)
    
    user = get_user(user_id)
    
    text = (
        f"✅ *Массовая продажа выполнена!*\n\n"
        f"🔥 Проданы дубликаты:\n"
        f"{chr(10).join(['• ' + card for card in sold_cards[:10]])}"
        f"{chr(10) + '• ...и ещё ' + str(len(sold_cards) - 10) if len(sold_cards) > 10 else ''}\n\n"
        f"🔄 Всего дубликатов: {total_duplicates}\n"
        f"💵 Получено: *{total_coins} монет*\n"
        f"💰 Новый баланс: *{user['coins']} монет*\n\n"
        f"📦 У всех карт осталось по 1 экземпляру."
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Назад к дубликатам", callback_data="sell_duplicates_menu|0")]]
    
    try:
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    except Exception as e:
        if "Message is not modified" in str(e):
            pass
        else:
            raise e


async def show_card_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("🔴 show_card_by_number ВЫЗВАНА!")
        
        query = update.callback_query
        print(f"🔴 query.data: {query.data}")
        
        try:
            await query.answer()
            print("✅ Ответили на callback")
        except Exception as e:
            print(f"❌ Ошибка при answer: {e}")
        
        user_id = update.effective_user.id
        chat_id = query.message.chat_id
        
        number = int(query.data.split("_")[2])
        print(f"🔍 Номер карты: {number}")
        
        hero_info = HEROES_BY_NUMBER.get(number)
        
        if not hero_info:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Герой с номером {number} не существует"
            )
            return
        
        description = hero_info.get("description", "⚠️ Описание отсутствует")
        
        collection = get_collection_with_duplicates(user_id)
        card = None
        duplicates = 0
        for hero in collection:
            if hero.get('card_number', 0) == number:
                card = hero
                duplicates = hero.get('duplicates', 1)
                break
        
        if card:
            try:
                print(f"🎴 Генерируем карточку для {hero_info['name']}")
                
                image_bytes = create_hero_card(hero_info)
                
                if hasattr(image_bytes, 'getvalue'):
                    image_data = image_bytes.getvalue()
                    print(f"✅ Карточка создана, размер: {len(image_data)} байт")
                else:
                    image_data = image_bytes
                    print(f"✅ Карточка создана")
                
                duplicate_text = ""
                keyboard = []
                
                if duplicates > 1:
                    duplicate_text = f"\n🔄 Дубликатов: {duplicates} шт."
                    keyboard.append([
                        InlineKeyboardButton(
                            "💰 Продать дубликаты",
                            callback_data=f"sell_duplicates_card|{number}"
                        )
                    ])
                
                keyboard.append([InlineKeyboardButton("🔙 Назад в альбом", callback_data="album_back")])
                
                caption = (
                    f"✅ **{hero_info['name']}**\n"
                    f"🆔 № {number:03d}\n"
                    f"✍️ {hero_info['author']}\n"
                    f"📚 {hero_info['book']}\n"
                    f"⭐ {hero_info.get('rarity', 'обычный').upper()}{duplicate_text}\n\n"
                    f"📝 *Описание:*\n{description}\n\n"
                    "🎉 Эта карта есть в вашем альбоме!"
                )
                
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=image_data,
                    caption=caption,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
                print(f"✅ Карточка отправлена в чат {chat_id}!")
            except Exception as e:
                print(f"❌ Ошибка при отправке карточки: {e}")
                traceback.print_exc()
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"❌ Ошибка при создании карточки для {hero_info['name']}"
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
                     f"📝 *Описание:*\n{description}\n\n"
                     "😔 Этого героя ещё нет в вашем альбоме!\n"
                     "Откройте паки, чтобы найти его.",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
            print(f"✅ Сообщение об отсутствии карты отправлено")
            
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в show_card_by_number: {e}")
        traceback.print_exc()
        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Произошла ошибка. Попробуйте позже."
            )
        except:
            pass


async def album_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        print("🟢 album_back вызван")
        query = update.callback_query
        await query.answer()
        await show_album(update, context)
    except Exception as e:
        print(f"❌ Ошибка в album_back: {e}")
        traceback.print_exc()