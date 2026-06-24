import random
import asyncio
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import (
    get_collection, get_user, update_duel_stats, add_coins
)
from ..friends import get_friends
from ..models.questions import QUESTIONS
from ..utils.helpers import extract_work

duels = {}
user_duel = {}
user_selection = {}
last_selection = {}

SAVE_CHANCES = {
    "легендарный": 12,
    "эпический": 9,
    "редкий": 6,
    "обычный": 3,
}

WORK_MULTIPLIERS = {
    "легендарный": 10,
    "эпический": 4,
    "редкий": 3,
    "обычный": 2,
}


def get_weighted_questions(selected_heroes, collection, all_questions, count=5):
    work_weights = defaultdict(int)
    for key in selected_heroes:
        hero = collection[key]
        work = hero.get("book", "")
        if work:
            work_weights[work] += WORK_MULTIPLIERS.get(hero.get("rarity", "обычный"), 1)

    weighted = []
    for q in all_questions:
        work = q.get("work", extract_work(q.get("text", "")))
        weight = work_weights.get(work, 1)
        weighted.append((q, weight))

    if count >= len(all_questions):
        return random.sample(all_questions, len(all_questions))

    pool = []
    for q, w in weighted:
        weight_int = int(w) if w >= 1 else 1
        pool.extend([q] * min(weight_int, 20))

    pool = pool[:1000]
    selected = []
    available = pool.copy()
    for _ in range(min(count, len(all_questions))):
        if not available:
            break
        chosen = random.choice(available)
        selected.append(chosen)
        available = [q for q in available if q != chosen]

    while len(selected) < count:
        remaining = [q for q in all_questions if q not in selected]
        if not remaining:
            break
        selected.append(random.choice(remaining))
    return selected


def get_save_chance(heroes, collection):
    return sum(SAVE_CHANCES.get(collection[k].get("rarity", "обычный"), 0) for k in heroes)


async def duel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception:
            pass
        user_id = query.from_user.id
        chat_id = query.message.chat_id
    else:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

    if user_id in user_duel:
        await context.bot.send_message(chat_id, "⚠️ У тебя уже есть активная дуэль! Используй /stopduel.")
        return

    collection = get_collection(user_id)
    if len(collection) < 3:
        await context.bot.send_message(chat_id, "❌ У тебя меньше 3 героев. Открой паки!")
        return

    keyboard = [
        [InlineKeyboardButton("👥 С друзьями", callback_data="duel_friends")],
        [InlineKeyboardButton("🤖 С ботом", callback_data="duel_bot")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    text = (
        "⚔️ *Выбери тип дуэли*\n\n"
        "👥 *С друзьями* — выбери друга из списка\n"
        "🤖 *С ботом* — сражайся против ИИ\n\n"
        "Для дуэли нужно *3 героя* в коллекции."
    )
    
    if query:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def duel_friends(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    friends = get_friends(user_id)
    
    if not friends:
        text = "😴 У вас пока нет друзей.\n\nДобавьте друзей через меню «Друзья»."
        keyboard = [
            [InlineKeyboardButton("👥 Добавить друзей", callback_data="friends_menu")],
            [InlineKeyboardButton("🔙 Назад", callback_data="duel")],
        ]
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    keyboard = []
    for fid in friends[:20]:
        try:
            chat = await context.bot.get_chat(fid)
            name = chat.first_name or f"ID: {fid}"
        except:
            name = f"ID: {fid}"
        
        hero_count = len(get_collection(fid))
        status = "🟢" if fid not in user_duel else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {name} ({hero_count} героев)", 
                callback_data=f"duel_friend_select|{fid}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="duel")])
    
    await query.edit_message_text(
        "👥 *Выбери друга для дуэли:*\n\n🟢 — доступен\n🔴 — в дуэли",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def duel_friend_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    friend_id = int(query.data.split("|")[1])

    if friend_id in user_duel:
        await query.edit_message_text("❌ Этот игрок уже в дуэли.")
        return

    if len(get_collection(friend_id)) < 3:
        await query.edit_message_text("❌ У этого игрока меньше 3 героев.")
        return

    keyboard = [
        [InlineKeyboardButton("✅ Принять дуэль", callback_data=f"duel_accept|{user_id}")],
        [InlineKeyboardButton("❌ Отказаться", callback_data="duel_decline")],
    ]
    await context.bot.send_message(
        friend_id, 
        f"⚔️ *{update.effective_user.first_name} хочет вызвать тебя на дуэль!*\n\n"
        f"Для дуэли нужно 3 героя в коллекции.",
        parse_mode="Markdown", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await query.edit_message_text("⏳ Отправлен запрос сопернику. Ожидай ответа...")


async def duel_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    opponent_id = int(query.data.split("|")[1])

    if opponent_id in user_duel:
        await query.edit_message_text("❌ Этот игрок уже в дуэли.")
        return

    if len(get_collection(user_id)) < 3 or len(get_collection(opponent_id)) < 3:
        await query.edit_message_text("❌ У одного из игроков меньше 3 героев.")
        return

    user_selection[user_id] = {"selected": [], "page": 0, "duel_type": "friend", "opponent": opponent_id}
    user_selection[opponent_id] = {"selected": [], "page": 0, "duel_type": "friend", "opponent": user_id}

    await context.bot.send_message(
        opponent_id,
        f"✅ *{update.effective_user.first_name}* принял ваше приглашение на дуэль!\n\nВыбирайте героев..."
    )

    await show_hero_selection_for_duel(update, context, user_id, query.message.chat_id, "friend")
    await show_hero_selection_for_duel(update, context, opponent_id, opponent_id, "friend")

    await query.edit_message_text("⚔️ *Дуэль принята! Выбирайте героев...*", parse_mode="Markdown")


async def duel_decline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Ты отказался от дуэли.")


async def duel_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if len(get_collection(user_id)) < 3:
        await context.bot.send_message(chat_id, "❌ У тебя меньше 3 героев. Открой паки!")
        return
    
    if user_id not in user_selection:
        user_selection[user_id] = {"selected": [], "page": 0, "duel_type": "bot", "opponent": None}
    
    await show_hero_selection_for_duel(update, context, user_id, chat_id, "bot")


async def show_hero_selection_for_duel(update, context, user_id, chat_id, duel_type):
    collection = get_collection(user_id)
    hero_keys = list(collection.keys())

    if user_id not in user_selection:
        user_selection[user_id] = {"selected": [], "page": 0, "duel_type": duel_type}

    data = user_selection[user_id]
    selected = data["selected"]
    page = data["page"]

    # Проверяем, есть ли сохраненный выбор
    has_last_selection = user_id in last_selection and len(last_selection[user_id]) == 3

    if len(hero_keys) <= 3:
        user_selection[user_id]["selected"] = hero_keys.copy()
        await start_duel_after_selection(update, context, user_id)
        return

    per_page = 5
    total_pages = (len(hero_keys) + per_page - 1) // per_page
    start = page * per_page
    end = min(start + per_page, len(hero_keys))

    keyboard = []
    
    # Кнопка "как в прошлый раз" - показываем ТОЛЬКО если есть сохраненный выбор
    if has_last_selection:
        valid_last_selection = []
        for hero_key in last_selection.get(user_id, []):
            if hero_key in collection:
                valid_last_selection.append(hero_key)
        
        if len(valid_last_selection) == 3:
            keyboard.append([
                InlineKeyboardButton(
                    "🔄 Выбрать как в прошлый раз", 
                    callback_data="hsel_last"
                )
            ])

    for i in range(start, end):
        hero = collection[hero_keys[i]]
        rarity = hero.get("rarity", "обычный")
        is_selected = hero_keys[i] in selected
        emoji = "✅" if is_selected else "⬜"
        save_chance = SAVE_CHANCES.get(rarity, 0)
        r_emoji = {"легендарный": "👑", "эпический": "⭐", "редкий": "🔵", "обычный": "📘"}.get(rarity, "📘")
        mult = WORK_MULTIPLIERS.get(rarity, 1)
        keyboard.append([InlineKeyboardButton(f"{emoji} {r_emoji} {hero['name'][:12]} (x{mult}, {save_chance}%)", callback_data=f"hsel|{i}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"hpage|{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"hpage|{page+1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton(f"📄 Страница {page+1}/{total_pages}", callback_data="noop")])
    keyboard.append([InlineKeyboardButton("⚔️ Начать дуэль", callback_data="startduel")])
    keyboard.append([InlineKeyboardButton("🔙 Отмена", callback_data="main_menu")])

    total_save = sum(SAVE_CHANCES.get(collection[k].get("rarity", "обычный"), 0) for k in selected)
    
    bonus_text = ""
    if selected:
        work_weights = defaultdict(int)
        for key in selected:
            hero = collection[key]
            work = hero.get("book", "")
            if work:
                work_weights[work] += WORK_MULTIPLIERS.get(hero.get("rarity", "обычный"), 1)
        
        if work_weights:
            bonus_text = "\n\n📚 *Бонусы к вопросам:*"
            for work, weight in work_weights.items():
                bonus_text += f"\n• {work}: x{weight}"
        
        bonus_text += f"\n\n🔄 *Шанс спасения:* {total_save}% (один раз)"

    text = f"⚔️ *Выбор героев для дуэли*\n\nВыбери *3 героя*\nВыбрано: {len(selected)}/3\n\n⬜ — не выбран, ✅ — выбран\nВ скобках: множитель и шанс спасения\n👑x10 12% ⭐x4 9% 🔵x3 6% 📘x2 3%{bonus_text}"

    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(f"❌ Ошибка отправки выбора героев: {e}")


async def show_hero_selection_edit(update, context, user_id, chat_id, duel_type):
    collection = get_collection(user_id)
    hero_keys = list(collection.keys())

    if user_id not in user_selection:
        user_selection[user_id] = {"selected": [], "page": 0, "duel_type": duel_type}

    data = user_selection[user_id]
    selected = data["selected"]
    page = data["page"]

    has_last_selection = user_id in last_selection and len(last_selection[user_id]) == 3

    if len(hero_keys) <= 3:
        user_selection[user_id]["selected"] = hero_keys.copy()
        await start_duel_after_selection(update, context, user_id)
        return

    per_page = 5
    total_pages = (len(hero_keys) + per_page - 1) // per_page
    start = page * per_page
    end = min(start + per_page, len(hero_keys))

    keyboard = []
    
    if has_last_selection:
        valid_last_selection = []
        for hero_key in last_selection.get(user_id, []):
            if hero_key in collection:
                valid_last_selection.append(hero_key)
        
        if len(valid_last_selection) == 3:
            keyboard.append([
                InlineKeyboardButton(
                    "🔄 Выбрать как в прошлый раз", 
                    callback_data="hsel_last"
                )
            ])

    for i in range(start, end):
        hero = collection[hero_keys[i]]
        rarity = hero.get("rarity", "обычный")
        is_selected = hero_keys[i] in selected
        emoji = "✅" if is_selected else "⬜"
        save_chance = SAVE_CHANCES.get(rarity, 0)
        r_emoji = {"легендарный": "👑", "эпический": "⭐", "редкий": "🔵", "обычный": "📘"}.get(rarity, "📘")
        mult = WORK_MULTIPLIERS.get(rarity, 1)
        keyboard.append([InlineKeyboardButton(f"{emoji} {r_emoji} {hero['name'][:12]} (x{mult}, {save_chance}%)", callback_data=f"hsel|{i}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"hpage|{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"hpage|{page+1}"))
    if nav:
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton(f"📄 Страница {page+1}/{total_pages}", callback_data="noop")])
    keyboard.append([InlineKeyboardButton("⚔️ Начать дуэль", callback_data="startduel")])
    keyboard.append([InlineKeyboardButton("🔙 Отмена", callback_data="main_menu")])

    total_save = sum(SAVE_CHANCES.get(collection[k].get("rarity", "обычный"), 0) for k in selected)
    
    bonus_text = ""
    if selected:
        work_weights = defaultdict(int)
        for key in selected:
            hero = collection[key]
            work = hero.get("book", "")
            if work:
                work_weights[work] += WORK_MULTIPLIERS.get(hero.get("rarity", "обычный"), 1)
        
        if work_weights:
            bonus_text = "\n\n📚 *Бонусы к вопросам:*"
            for work, weight in work_weights.items():
                bonus_text += f"\n• {work}: x{weight}"
        
        bonus_text += f"\n\n🔄 *Шанс спасения:* {total_save}% (один раз)"

    text = f"⚔️ *Выбор героев для дуэли*\n\nВыбери *3 героя*\nВыбрано: {len(selected)}/3\n\n⬜ — не выбран, ✅ — выбран\nВ скобках: множитель и шанс спасения\n👑x10 12% ⭐x4 9% 🔵x3 6% 📘x2 3%{bonus_text}"

    try:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(f"❌ Ошибка редактирования выбора героев: {e}")


async def handle_hero_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        return

    data = query.data
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if data == "hsel_last":
        # Проверяем, есть ли сохраненный выбор
        if user_id in last_selection and len(last_selection[user_id]) == 3:
            # Проверяем, все ли герои из прошлого выбора есть в коллекции
            collection = get_collection(user_id)
            valid_selection = []
            for hero_key in last_selection[user_id]:
                if hero_key in collection:
                    valid_selection.append(hero_key)
            
            if len(valid_selection) == 3:
                user_selection[user_id]["selected"] = valid_selection.copy()
                await query.edit_message_text("✅ Использован прошлый выбор героев!")
                await show_hero_selection_edit(update, context, user_id, chat_id, user_selection[user_id].get("duel_type", "friend"))
            else:
                await query.edit_message_text("❌ Некоторые герои из прошлого выбора больше не доступны.")
        else:
            await query.edit_message_text("❌ Нет сохранённого выбора героев.")
        return

    if data.startswith("hsel|"):
        idx = int(data.split("|")[1])
        collection = get_collection(user_id)
        hero_keys = list(collection.keys())
        if idx >= len(hero_keys):
            return

        user_data = user_selection.get(user_id, {"selected": [], "page": 0})
        selected = user_data["selected"]
        hero_key = hero_keys[idx]

        if hero_key in selected:
            selected.remove(hero_key)
        elif len(selected) < 3:
            selected.append(hero_key)
        else:
            await query.answer("❌ Ты уже выбрал 3 героев!", show_alert=True)
            return

        user_selection[user_id]["selected"] = selected
        if len(selected) == 3:
            last_selection[user_id] = selected.copy()
        
        await show_hero_selection_edit(update, context, user_id, chat_id, user_data.get("duel_type", "friend"))
        return

    elif data.startswith("hpage|"):
        page = int(data.split("|")[1])
        user_selection[user_id]["page"] = page
        await show_hero_selection_edit(update, context, user_id, chat_id, user_selection[user_id].get("duel_type", "friend"))
        return

    elif data == "startduel":
        selected = user_selection.get(user_id, {}).get("selected", [])
        if len(selected) != 3:
            await query.answer("❌ Выбери ровно 3 героев!", show_alert=True)
            return
        await start_duel_after_selection(update, context, user_id)

    elif data == "main_menu":
        user_selection.pop(user_id, None)
        from .start import start
        await start(update, context)


async def start_duel_after_selection(update, context, user_id):
    data = user_selection.get(user_id, {})
    selected = data.get("selected", [])
    duel_type = data.get("duel_type", "friend")
    opponent_id = data.get("opponent")

    if len(selected) != 3:
        return

    if duel_type == "bot":
        await start_bot_duel(update, context, user_id, selected)
        return

    if opponent_id:
        opponent_data = user_selection.get(opponent_id, {})
        opponent_selected = opponent_data.get("selected", [])
        
        if len(opponent_selected) != 3:
            await context.bot.send_message(
                user_id,
                "⏳ Ожидаем выбора героев от соперника..."
            )
            return
        
        await start_duel(update, context, user_id, opponent_id, selected, opponent_selected)
        return

    user_selection.pop(user_id, None)
    await context.bot.send_message(user_id, "❌ Ошибка поиска соперника. Попробуй ещё раз.")


async def start_duel(update, context, user_id, opponent_id, p1_chosen, p2_chosen):
    collection = get_collection(user_id)
    p2_collection = get_collection(opponent_id)
    questions = get_weighted_questions(p1_chosen, collection, QUESTIONS, 5)

    p1_save = get_save_chance(p1_chosen, collection)
    p2_save = get_save_chance(p2_chosen, p2_collection)

    duel_id = f"{user_id}_{opponent_id}_{random.randint(1000,9999)}"
    duels[duel_id] = {
        "player1": user_id, "player2": opponent_id, "status": "active",
        "p1_score": 0, "p2_score": 0,
        "questions": questions, "turn": 0,
        "p1_chosen": p1_chosen, "p2_chosen": p2_chosen,
        "question_active": False,
        "waiting_for_answer": False,
        "p1_save_chance": p1_save, "p2_save_chance": p2_save,
        "p1_save_used": False, "p2_save_used": False,
        "p1_answered": False, "p2_answered": False,
    }

    user_duel[user_id] = duel_id
    user_duel[opponent_id] = duel_id

    p1_names = [collection[k]['name'] for k in p1_chosen]
    p2_names = [p2_collection[k]['name'] for k in p2_chosen]

    await context.bot.send_message(user_id, f"⚔️ *Дуэль началась!*\nТвои герои: {', '.join(p1_names)}\n🔄 Шанс спасения: {p1_save}%\n\nВсего вопросов: 5\nКто первый ответит правильно — получает очко!", parse_mode="Markdown")
    await context.bot.send_message(opponent_id, f"⚔️ *Дуэль началась!*\nТвои герои: {', '.join(p2_names)}\n🔄 Шанс спасения: {p2_save}%\n\nВсего вопросов: 5\nКто первый ответит правильно — получает очко!", parse_mode="Markdown")

    user_selection.pop(user_id, None)
    user_selection.pop(opponent_id, None)
    
    await asyncio.sleep(1)
    await ask_question_friend(update, context, duel_id)


async def start_bot_duel(update, context, user_id, p1_chosen):
    collection = get_collection(user_id)
    from ..models.hero import HEROES
    
    bot_heroes = random.sample(HEROES, 3)

    questions = get_weighted_questions(p1_chosen, collection, QUESTIONS, 5)
    p1_save = get_save_chance(p1_chosen, collection)

    duel_id = f"{user_id}_bot_{random.randint(1000,9999)}"
    duels[duel_id] = {
        "player1": user_id, "player2": "bot", "status": "active",
        "p1_score": 0, "p2_score": 0,
        "questions": questions, "turn": 0,
        "p1_chosen": p1_chosen, "p2_chosen": [h['name'] for h in bot_heroes],
        "question_active": False,
        "waiting_for_answer": False,
        "is_bot": True,
        "p1_save_chance": p1_save, "p2_save_chance": 0,
        "p1_save_used": False, "p2_save_used": False,
    }

    user_duel[user_id] = duel_id
    p1_names = [collection[k]['name'] for k in p1_chosen]
    p2_names = [h['name'] for h in bot_heroes]

    await context.bot.send_message(user_id,
        f"🤖 *Дуэль с ботом началась!*\nТвои герои: {', '.join(p1_names)}\nГерои бота: {', '.join(p2_names)}\n🔄 Шанс спасения: {p1_save}%\n\n"
        f"✅ Правильно → +1 очко тебе\n❌ Неправильно → +1 очко боту\n"
        f"🔄 Если ответишь неправильно, есть шанс спасения (макс 1 раз за дуэль)",
        parse_mode="Markdown")

    user_selection.pop(user_id, None)
    
    await asyncio.sleep(1)
    await ask_question_bot(update, context, duel_id)


async def ask_question_bot(update, context, duel_id):
    """Вопрос для дуэли с ботом"""
    duel = duels.get(duel_id)
    if not duel or duel["status"] != "active":
        return

    if duel["turn"] >= len(duel["questions"]):
        await finish_duel(update, context, duel_id)
        return

    q = duel["questions"][duel["turn"]]
    
    duel["question_active"] = True
    duel["waiting_for_answer"] = True

    work = q.get("work", extract_work(q.get("text", "")))
    work_text = f"\n📖 *{work}*" if work else ""

    keyboard = [[InlineKeyboardButton(opt, callback_data=f"b|{duel_id}|{i}")] for i, opt in enumerate(q["options"])]
    text = f"❓ *Вопрос {duel['turn'] + 1} из 5*\n\n{q['text']}{work_text}\n\n_Выбери вариант ответа:_"

    await context.bot.send_message(
        duel["player1"], 
        text, 
        parse_mode="Markdown", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ask_question_friend(update, context, duel_id):
    """Вопрос для дуэли с другом - кто первый ответит"""
    duel = duels.get(duel_id)
    if not duel or duel["status"] != "active":
        return

    if duel["turn"] >= len(duel["questions"]):
        await finish_duel(update, context, duel_id)
        return

    q = duel["questions"][duel["turn"]]
    
    duel["question_active"] = True
    duel["waiting_for_answer"] = True
    duel["p1_answered"] = False
    duel["p2_answered"] = False

    work = q.get("work", extract_work(q.get("text", "")))
    work_text = f"\n📖 *{work}*" if work else ""

    keyboard = [[InlineKeyboardButton(opt, callback_data=f"f|{duel_id}|{i}")] for i, opt in enumerate(q["options"])]
    text = f"❓ *Вопрос {duel['turn'] + 1} из 5*\n\n{q['text']}{work_text}\n\n_Кто первый ответит правильно — получит очко!_"

    # Отправляем вопрос ОБОИМ игрокам
    await context.bot.send_message(
        duel["player1"], 
        text, 
        parse_mode="Markdown", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await context.bot.send_message(
        duel["player2"], 
        text, 
        parse_mode="Markdown", 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        return

    data = query.data
    if not data.startswith("b|") and not data.startswith("f|"):
        return

    parts = data.split("|")
    duel_type = parts[0]
    duel_id = parts[1]
    answer_idx = int(parts[2])
    
    duel = duels.get(duel_id)
    if not duel or duel["status"] != "active":
        await query.edit_message_text("❌ Дуэль уже завершена.")
        return

    if not duel.get("waiting_for_answer") or duel.get("question_active") == False:
        await query.edit_message_text("⏳ Этот вопрос уже завершён!")
        return

    if duel["turn"] >= len(duel["questions"]):
        await query.edit_message_text("❌ Дуэль уже завершена.")
        return

    player_id = update.effective_user.id
    
    if duel_type == "b":
        # ДУЭЛЬ С БОТОМ
        await handle_bot_answer(update, context, duel_id, player_id, answer_idx)
    else:
        # ДУЭЛЬ С ДРУГОМ
        await handle_friend_answer(update, context, duel_id, player_id, answer_idx)


async def handle_bot_answer(update, context, duel_id, player_id, answer_idx):
    """Обработка ответа в дуэли с ботом"""
    duel = duels.get(duel_id)
    if not duel:
        return
    
    # Блокируем вопрос
    duel["question_active"] = False
    duel["waiting_for_answer"] = False

    q = duel["questions"][duel["turn"]]
    is_correct = answer_idx == q["correct"]
    correct_text = q["options"][q["correct"]]

    if is_correct:
        # Правильно → +1 очко игроку
        duel["p1_score"] += 1
        await update.callback_query.edit_message_text("✅ *Правильно!* +1 очко!", parse_mode="Markdown")
        
        await context.bot.send_message(
            duel["player1"], 
            f"✅ *Правильный ответ:* {correct_text}", 
            parse_mode="Markdown"
        )
        
        await asyncio.sleep(1.5)
        duel["turn"] += 1
        await ask_question_bot(update, context, duel_id)
        
    else:
        # Неправильно → проверяем спасение
        save_chance = duel.get("p1_save_chance", 0)
        save_used = duel.get("p1_save_used", False)

        if not save_used and save_chance > 0 and random.random() * 100 < save_chance:
            # Спасение сработало
            duel["p1_score"] += 1
            duel["p1_save_used"] = True
            await update.callback_query.edit_message_text(
                f"🔄 *Спасение!*\nОтвет был неправильным, но герои спасли тебя! +1 очко! (шанс {save_chance}%)", 
                parse_mode="Markdown"
            )
            
            await context.bot.send_message(
                duel["player1"], 
                f"✅ *Правильный ответ:* {correct_text}", 
                parse_mode="Markdown"
            )
            
            await asyncio.sleep(1.5)
            duel["turn"] += 1
            await ask_question_bot(update, context, duel_id)
            return

        # Спасение не сработало → +1 очко боту
        duel["p2_score"] += 1
        await update.callback_query.edit_message_text("❌ *Неправильно.* +1 очко боту!", parse_mode="Markdown")
        
        await context.bot.send_message(
            duel["player1"], 
            f"✅ *Правильный ответ:* {correct_text}", 
            parse_mode="Markdown"
        )
        
        await asyncio.sleep(1.5)
        duel["turn"] += 1
        await ask_question_bot(update, context, duel_id)


async def handle_friend_answer(update, context, duel_id, player_id, answer_idx):
    """Обработка ответа в дуэли с другом - кто первый"""
    duel = duels.get(duel_id)
    if not duel:
        return
    
    # Проверяем, кто уже отвечал
    is_p1 = player_id == duel["player1"]
    player_key = "p1" if is_p1 else "p2"
    
    if duel.get(f"{player_key}_answered"):
        await update.callback_query.edit_message_text("⏳ Ты уже отвечал на этот вопрос!")
        return
    
    # Сохраняем ответ
    duel[f"{player_key}_answered"] = True
    
    q = duel["questions"][duel["turn"]]
    is_correct = answer_idx == q["correct"]
    
    if not is_correct:
        await update.callback_query.edit_message_text("❌ *Неправильно!*", parse_mode="Markdown")
        return
    
    # Проверяем, не ответил ли уже соперник правильно
    other_key = "p2" if is_p1 else "p1"
    if duel.get(f"{other_key}_score_increment"):
        await update.callback_query.edit_message_text("⏳ Соперник уже ответил правильно на этот вопрос!")
        return
    
    # Игрок ответил правильно → +1 очко
    duel[f"{player_key}_score"] += 1
    duel[f"{player_key}_score_increment"] = True
    
    # Блокируем вопрос
    duel["question_active"] = False
    duel["waiting_for_answer"] = False
    
    correct_text = q["options"][q["correct"]]
    
    await update.callback_query.edit_message_text("✅ *Правильно!* +1 очко!", parse_mode="Markdown")
    
    # Уведомляем обоих игроков
    await context.bot.send_message(
        duel["player1"], 
        f"✅ *Правильный ответ:* {correct_text}\n\n*{update.effective_user.first_name}* ответил первым и получает очко!",
        parse_mode="Markdown"
    )
    await context.bot.send_message(
        duel["player2"], 
        f"✅ *Правильный ответ:* {correct_text}\n\n*{update.effective_user.first_name}* ответил первым и получает очко!",
        parse_mode="Markdown"
    )
    
    await asyncio.sleep(1.5)
    duel["turn"] += 1
    await ask_question_friend(update, context, duel_id)


async def finish_duel(update, context, duel_id):
    duel = duels.get(duel_id)
    if not duel:
        return

    duel["status"] = "finished"
    p1, p2 = duel["player1"], duel["player2"]
    p1_score, p2_score = duel["p1_score"], duel["p2_score"]
    is_bot = duel.get("is_bot", False)

    if p1_score > p2_score:
        add_coins(p1, 20)
        update_duel_stats(p1, True)
        if not is_bot:
            update_duel_stats(p2, False)
            await context.bot.send_message(p2, f"😔 *Ты проиграл.* {p1_score}:{p2_score}", parse_mode="Markdown")
        await context.bot.send_message(p1, f"🏆 *Ты победил!* +20 монет!\n{p1_score}:{p2_score}", parse_mode="Markdown")
    elif p2_score > p1_score:
        if is_bot:
            await context.bot.send_message(p1, f"🤖 *Бот победил!*\n{p2_score}:{p1_score}\n\nПопробуй ещё раз!", parse_mode="Markdown")
        else:
            add_coins(p2, 20)
            update_duel_stats(p2, True)
            update_duel_stats(p1, False)
            await context.bot.send_message(p2, f"🏆 *Ты победил!* +20 монет!\n{p2_score}:{p1_score}", parse_mode="Markdown")
            await context.bot.send_message(p1, f"😔 *Ты проиграл.*\n{p2_score}:{p1_score}", parse_mode="Markdown")
    else:
        if is_bot:
            await context.bot.send_message(p1, f"🤝 *Ничья с ботом!*\n{p1_score}:{p2_score}", parse_mode="Markdown")
        else:
            add_coins(p1, 5)
            add_coins(p2, 5)
            await context.bot.send_message(p1, f"🤝 *Ничья!* +5 монет каждому\n{p1_score}:{p2_score}", parse_mode="Markdown")
            await context.bot.send_message(p2, f"🤝 *Ничья!* +5 монет каждому\n{p2_score}:{p1_score}", parse_mode="Markdown")

    for pid in [p1, p2]:
        if pid in user_duel and pid != "bot":
            del user_duel[pid]
        if pid in user_selection:
            del user_selection[pid]
    duels.pop(duel_id, None)


async def stop_duel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_duel:
        await update.message.reply_text("❌ У тебя нет активной дуэли.")
        return

    duel_id = user_duel[user_id]
    duel = duels.get(duel_id)
    if not duel:
        del user_duel[user_id]
        await update.message.reply_text("❌ Дуэль уже завершена.")
        return

    if duel.get("is_bot"):
        await context.bot.send_message(duel["player1"], "🤖 Бот победил! Ты завершил дуэль командой /stopduel.")
    else:
        winner = duel["player2"] if user_id == duel["player1"] else duel["player1"]
        loser = duel["player1"] if user_id == duel["player1"] else duel["player2"]
        add_coins(winner, 5)
        update_duel_stats(winner, True)
        update_duel_stats(loser, False)
        await context.bot.send_message(winner, f"🏆 *Ты победил!* Соперник завершил дуэль командой /stopduel.", parse_mode="Markdown")
        await context.bot.send_message(loser, f"😔 *Ты завершил дуэль командой /stopduel.*", parse_mode="Markdown")

    for pid in [duel["player1"], duel["player2"]]:
        if pid in user_duel and pid != "bot":
            del user_duel[pid]
    duels.pop(duel_id, None)
    await update.message.reply_text("🏳️ *Дуэль завершена командой /stopduel.*", parse_mode="Markdown")


def cancel_duel(duel_id: str):
    duel = duels.pop(duel_id, None)
    if duel:
        for pid in [duel.get("player1"), duel.get("player2")]:
            if pid in user_duel and pid != "bot":
                del user_duel[pid]
            if pid in user_selection:
                del user_selection[pid]