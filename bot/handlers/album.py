from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection
from ..models.hero import HEROES_BY_NUMBER, get_total_heroes
from ..utils.image_generator import create_hero_card
import logging
import traceback

logger = logging.getLogger(__name__)

CARDS_PER_PAGE = 8


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
        
        collection = get_collection(user_id)
        print(f"📊 Коллекция пользователя {user_id}: {len(collection)} карт")
        
        collected_numbers = set()
        for hero in collection.values():
            number = hero.get('card_number', 0)
            if number > 0:
                collected_numbers.add(number)
        
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
        
        collection = get_collection(user_id)
        
        card = None
        for hero in collection.values():
            if hero.get('card_number', 0) == number:
                card = hero
                break
        
        # БЕРЁМ ГЕРОЯ ИЗ hero.py ПО НОМЕРУ
        hero_info = HEROES_BY_NUMBER.get(number)
        
        print(f"📊 card из БД: {card is not None}")
        print(f"📊 hero_info: {hero_info.get('name') if hero_info else None}")
        
        if not hero_info:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Герой с номером {number} не существует"
            )
            return
        
        # БЕРЕМ ОПИСАНИЕ ИЗ hero.py (БЕЗ ЗАПАСНОГО ВАРИАНТА)
        description = hero_info.get("description")
        
        # Если описания нет — пишем что отсутствует
        if not description:
            description = "⚠️ Описание отсутствует"
        
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
                
                caption = (
                    f"✅ **{hero_info['name']}**\n"
                    f"🆔 № {number:03d}\n"
                    f"✍️ {hero_info['author']}\n"
                    f"📚 {hero_info['book']}\n"
                    f"⭐ {hero_info.get('rarity', 'обычный').upper()}\n\n"
                    f"📝 *Описание:*\n{description}\n\n"
                    "🎉 Эта карта есть в вашем альбоме!"
                )
                
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=image_data,
                    caption=caption,
                    parse_mode="Markdown"
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