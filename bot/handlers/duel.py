import random
import asyncio
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection, get_user, update_duel_stats, get_opponent, get_all_users
from ..models.questions import QUESTIONS
from ..utils.helpers import shuffle_question, extract_work

duels = {}
user_duel = {}
user_selection = {}

BONUSES = {
    "обычный": {"name": "Уверенность", "code": "b1"},
    "редкий": {"name": "Подсказка", "code": "b2"},
    "эпический": {"name": "Пересдача", "code": "b3"},
    "легендарный": {"name": "Автопобеда", "code": "b4"},
}

WORK_MULTIPLIERS = {
    "легендарный": 10,
    "эпический": 4,
    "редкий": 3,
    "обычный": 2,
}


def get_weighted_questions(selected_heroes, collection, all_questions, count=5):
    work_weights = defaultdict(int)
    
    for hero_key in selected_heroes:
        hero = collection[hero_key]
        rarity = hero.get("rarity", "обычный")
        work = hero.get("book", "")
        if work:
            work_weights[work] += WORK_MULTIPLIERS.get(rarity, 1)
    
    weighted_questions = []
    for q in all_questions:
        work = q.get("work", "")
        if not work:
            work = extract_work(q.get("text", ""))
        weight = work_weights.get(work, 1)
        weighted_questions.append((q, weight))
    
    if count >= len(all_questions):
        return random.sample(all_questions, len(all_questions))
    
    pool = []
    for q, weight in weighted_questions:
        pool.extend([q] * min(weight, 20))
    
    if len(pool) > 1000:
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


async def duel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню выбора типа дуэли"""
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
        [InlineKeyboardButton("🎲 Случайный соперник", callback_data="duel_random")],
        [InlineKeyboardButton("👤 С другом", callback_data="duel_friend")],
        [InlineKeyboardButton("🤖 С ботом", callback_data="duel_bot")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    
    text = (
        f"⚔️ *Выбери тип дуэли*\n\n"
        f"🎲 *Случайный соперник* — найди случайного игрока\n"
        f"👤 *С другом* — выбери друга из списка\n"
        f"🤖 *С ботом* — сражайся против ИИ\n\n"
        f"Для дуэли нужно *3 героя* в коллекции."
    )
    
    if query:
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def duel_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает дуэль со случайным соперником"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    await start_duel_with_opponent(update, context, user_id, chat_id, "random")


async def duel_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список друзей для выбора"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    all_users = get_all_users()
    available_users = [u for u in all_users if u["user_id"] != user_id]
    
    if not available_users:
        await query.edit_message_text("😴 Нет других игроков. Попробуй позже.")
        return
    
    keyboard = []
    for user in available_users[:20]:
        try:
            chat = await context.bot.get_chat(user["user_id"])
            name = chat.first_name or f"ID: {user['user_id']}"
        except:
            name = f"ID: {user['user_id']}"
        
        collection = get_collection(user["user_id"])
        hero_count = len(collection)
        keyboard.append([InlineKeyboardButton(
            f"👤 {name} ({hero_count} героев)",
            callback_data=f"duel_friend_select|{user['user_id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="duel")])
    
    text = "👤 *Выбери друга для дуэли:*\n\n_Показаны первые 20 пользователей_"
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def duel_friend_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор конкретного друга для дуэли"""
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split("|")
    user_id = query.from_user.id
    friend_id = int(parts[1])
    
    if friend_id in user_duel:
        await query.edit_message_text("❌ Этот игрок уже в дуэли.")
        return
    
    friend_collection = get_collection(friend_id)
    if len(friend_collection) < 3:
        await query.edit_message_text("❌ У этого игрока меньше 3 героев.")
        return
    
    await start_duel_with_opponent(update, context, user_id, query.message.chat_id, "friend", friend_id)


async def duel_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает дуэль с ботом"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    await start_duel_with_bot(update, context, user_id, chat_id)


async def start_duel_with_opponent(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int, mode: str, opponent_id: int = None):
    """Запускает дуэль с соперником (рандом или друг)"""
    collection = get_collection(user_id)
    
    if mode == "friend" and opponent_id:
        keyboard = [
            [InlineKeyboardButton("✅ Принять дуэль", callback_data=f"duel_accept|{user_id}")],
            [InlineKeyboardButton("❌ Отказаться", callback_data="duel_decline")],
        ]
        
        await context.bot.send_message(
            opponent_id,
            f"⚔️ *{update.effective_user.first_name} хочет вызвать тебя на дуэль!*\n\n"
            f"Принять вызов?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        await context.bot.send_message(
            chat_id,
            "⏳ Отправлен запрос сопернику. Ожидай ответа..."
        )
        return
    
    if mode == "random":
        opponent_id = get_opponent(user_id)
        if not opponent_id:
            await context.bot.send_message(chat_id, "😴 Нет других игроков. Попробуй позже.")
            return
        
        if opponent_id in user_duel:
            await context.bot.send_message(chat_id, "Соперник уже в игре.")
            return
    
    await proceed_to_hero_selection(update, context, user_id, chat_id, opponent_id)


async def duel_accept(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Принятие дуэли с другом"""
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split("|")
    opponent_id = int(parts[1])
    user_id = query.from_user.id
    
    if opponent_id in user_duel:
        await query.edit_message_text("❌ Этот игрок уже в дуэли.")
        return
    
    user_collection = get_collection(user_id)
    opponent_collection = get_collection(opponent_id)
    
    if len(user_collection) < 3 or len(opponent_collection) < 3:
        await query.edit_message_text("❌ У одного из игроков меньше 3 героев.")
        return
    
    await proceed_to_hero_selection(update, context, user_id, query.message.chat_id, opponent_id, initiator=opponent_id)


async def duel_decline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отказ от дуэли с другом"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Ты отказался от дуэли.")


async def proceed_to_hero_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int, opponent_id: int, initiator: int = None):
    """Переход к выбору героев"""
    user_selection[user_id] = {
        "selected": [],
        "page": 0,
        "opponent": opponent_id,
        "initiator": initiator or user_id,
        "mode": "friend" if initiator else "random",
    }
    
    await show_hero_selection(update, context, user_id, chat_id)


async def show_hero_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int):
    collection = get_collection(user_id)
    hero_keys = list(collection.keys())
    user_data = user_selection.get(user_id, {"selected": [], "page": 0})
    selected = user_data.get("selected", [])
    page = user_data.get("page", 0)
    
    if len(hero_keys) <= 3:
        user_selection[user_id]["selected"] = hero_keys.copy()
        await start_duel_after_selection(update, context, user_id)
        return
    
    per_page = 5
    total_pages = (len(hero_keys) + per_page - 1) // per_page
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(hero_keys))
    
    keyboard = []
    
    for i in range(start_idx, end_idx):
        key = hero_keys[i]
        hero = collection[key]
        rarity = hero.get("rarity", "обычный")
        is_selected = key in selected
        
        rarity_emoji = {
            "легендарный": "👑",
            "эпический": "⭐",
            "редкий": "🔵",
            "обычный": "📘"
        }.get(rarity, "📘")
        
        selected_emoji = "✅" if is_selected else "⬜"
        mult = WORK_MULTIPLIERS.get(rarity, 1)
        keyboard.append([InlineKeyboardButton(
            f"{selected_emoji} {rarity_emoji} {hero['name'][:18]} (x{mult})",
            callback_data=f"hsel|{i}"
        )])
    
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"hpage|{page-1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"hpage|{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    
    if total_pages > 1:
        keyboard.append([InlineKeyboardButton(
            f"📄 Страница {page+1}/{total_pages}",
            callback_data="noop"
        )])
    
    keyboard.append([InlineKeyboardButton("⚔️ Начать дуэль", callback_data="startduel")])
    keyboard.append([InlineKeyboardButton("🔙 Отмена", callback_data="main_menu")])
    
    selected_count = len(selected)
    
    bonus_text = ""
    if selected:
        work_weights = defaultdict(int)
        for key in selected:
            hero = collection[key]
            rarity = hero.get("rarity", "обычный")
            work = hero.get("book", "")
            if work:
                work_weights[work] += WORK_MULTIPLIERS.get(rarity, 1)
        
        if work_weights:
            bonus_text = "\n\n📚 *Бонусы к вопросам:*"
            for work, weight in work_weights.items():
                bonus_text += f"\n• {work}: x{weight}"
    
    text = (
        f"⚔️ *Выбор героев для дуэли*\n\n"
        f"Выбери *3 героя*, которые будут участвовать в дуэли.\n"
        f"Выбрано: {selected_count}/3\n\n"
        f"⬜ — не выбран, ✅ — выбран\n"
        f"👑 x10  ⭐ x4  🔵 x3  📘 x2\n"
        f"(шанс выпадения вопросов по их произведениям)"
        f"{bonus_text}"
    )
    
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await context.bot.send_message(
                chat_id,
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    except Exception as e:
        print(f"⚠️ Ошибка при показе выбора героев: {e}")


async def handle_hero_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        print(f"⚠️ Устаревшая кнопка: {e}")
        return
    
    data = query.data
    user_id = query.from_user.id
    
    if data.startswith("hsel|"):
        try:
            hero_idx = int(data.split("|")[1])
        except (IndexError, ValueError):
            return
        
        collection = get_collection(user_id)
        hero_keys = list(collection.keys())
        if hero_idx >= len(hero_keys):
            return
        
        hero_key = hero_keys[hero_idx]
        user_data = user_selection.get(user_id, {"selected": [], "page": 0})
        selected = user_data.get("selected", [])
        
        if hero_key in selected:
            selected.remove(hero_key)
        else:
            if len(selected) >= 3:
                try:
                    await query.answer("❌ Ты уже выбрал 3 героев!", show_alert=True)
                except Exception:
                    pass
                return
            selected.append(hero_key)
        
        user_selection[user_id]["selected"] = selected
        await show_hero_selection(update, context, user_id, query.message.chat_id)
    
    elif data.startswith("hpage|"):
        try:
            page = int(data.split("|")[1])
        except (IndexError, ValueError):
            return
        
        user_selection[user_id]["page"] = page
        await show_hero_selection(update, context, user_id, query.message.chat_id)
    
    elif data == "startduel":
        user_data = user_selection.get(user_id, {"selected": [], "page": 0})
        selected = user_data.get("selected", [])
        
        if len(selected) != 3:
            try:
                await query.answer("❌ Выбери ровно 3 героев!", show_alert=True)
            except Exception:
                pass
            return
        
        await start_duel_after_selection(update, context, user_id)
    
    elif data == "main_menu":
        user_selection.pop(user_id, None)
        from .start import start
        await start(update, context)


async def start_duel_after_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    collection = get_collection(user_id)
    user_data = user_selection.get(user_id, {"selected": [], "page": 0})
    selected_heroes = user_data.get("selected", [])
    opponent_id = user_data.get("opponent")
    
    if len(selected_heroes) != 3:
        await show_hero_selection(update, context, user_id, update.effective_chat.id)
        return
    
    p2_collection = get_collection(opponent_id)
    p2_keys = list(p2_collection.keys())
    
    rarity_order = {"легендарный": 0, "эпический": 1, "редкий": 2, "обычный": 3}
    sorted_p2_keys = sorted(p2_keys, key=lambda k: rarity_order.get(p2_collection[k].get("rarity", "обычный"), 4))
    p2_chosen = sorted_p2_keys[:3] if len(sorted_p2_keys) >= 3 else random.sample(p2_keys, 3)
    
    p1_chosen = selected_heroes
    
    questions = get_weighted_questions(p1_chosen, collection, QUESTIONS, 5)
    
    duel_id = f"{user_id}_{opponent_id}_{random.randint(1000,9999)}"
    
    duels[duel_id] = {
        "player1": user_id,
        "player2": opponent_id,
        "status": "active",
        "p1_score": 0,
        "p2_score": 0,
        "p1_used": [],
        "p2_used": [],
        "questions": questions,
        "turn": 0,
        "current_player": user_id,
        "p1_chosen": p1_chosen,
        "p2_chosen": p2_chosen,
        "question_active": False,
        "correct_answered": False,
        "p1_answered": False,
        "p2_answered": False,
        "waiting_for_answer": False,
    }
    
    user_duel[user_id] = duel_id
    user_duel[opponent_id] = duel_id
    
    p1_names = [collection[k]['name'] for k in p1_chosen]
    p2_names = [p2_collection[k]['name'] for k in p2_chosen]
    
    await context.bot.send_message(
        user_id,
        f"⚔️ *Дуэль началась!*\n"
        f"Твои герои: {', '.join(p1_names)}\n\n"
        f"Всего вопросов: 5\n\n"
        f"За каждый правильный ответ — 1 очко.",
        parse_mode="Markdown"
    )
    
    await context.bot.send_message(
        opponent_id,
        f"⚔️ *Дуэль началась!*\n"
        f"Твои герои: {', '.join(p2_names)}\n\n"
        f"Всего вопросов: 5\n\n"
        f"За каждый правильный ответ — 1 очко.",
        parse_mode="Markdown"
    )
    
    user_selection.pop(user_id, None)
    await ask_question(update, context, duel_id)


async def start_duel_with_bot(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int):
    """Запускает дуэль с ботом"""
    collection = get_collection(user_id)
    hero_keys = list(collection.keys())
    
    if len(hero_keys) < 3:
        await context.bot.send_message(chat_id, "❌ У тебя меньше 3 героев. Открой паки!")
        return
    
    rarity_order = {"легендарный": 0, "эпический": 1, "редкий": 2, "обычный": 3}
    sorted_keys = sorted(hero_keys, key=lambda k: rarity_order.get(collection[k].get("rarity", "обычный"), 4))
    p1_chosen = sorted_keys[:3] if len(sorted_keys) >= 3 else random.sample(hero_keys, 3)
    
    from ..models.hero import HEROES
    bot_heroes = random.sample(HEROES, 3)
    
    bot_collection = {}
    for hero in bot_heroes:
        key = f"bot_{hero['name']}"
        bot_collection[key] = hero
    
    p2_chosen = list(bot_collection.keys())
    
    questions = get_weighted_questions(p1_chosen, collection, QUESTIONS, 5)
    
    duel_id = f"{user_id}_bot_{random.randint(1000,9999)}"
    
    duels[duel_id] = {
        "player1": user_id,
        "player2": "bot",
        "status": "active",
        "p1_score": 0,
        "p2_score": 0,
        "p1_used": [],
        "p2_used": [],
        "questions": questions,
        "turn": 0,
        "current_player": user_id,
        "p1_chosen": p1_chosen,
        "p2_chosen": p2_chosen,
        "question_active": False,
        "correct_answered": False,
        "p1_answered": False,
        "p2_answered": False,
        "waiting_for_answer": False,
        "is_bot": True,
    }
    
    user_duel[user_id] = duel_id
    
    p1_names = [collection[k]['name'] for k in p1_chosen]
    p2_names = [hero['name'] for hero in bot_heroes]
    
    await context.bot.send_message(
        user_id,
        f"🤖 *Дуэль с ботом началась!*\n"
        f"Твои герои: {', '.join(p1_names)}\n"
        f"Герои бота: {', '.join(p2_names)}\n\n"
        f"Всего вопросов: 5\n\n"
        f"За каждый правильный ответ — 1 очко.",
        parse_mode="Markdown"
    )
    
    await ask_question(update, context, duel_id)


def get_bot_answer(question):
    """Бот даёт правильный ответ с вероятностью 70%"""
    if random.random() < 0.7:
        return question["correct"]
    else:
        options = list(range(len(question["options"])))
        options.remove(question["correct"])
        return random.choice(options)


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE, duel_id: str):
    duel = duels.get(duel_id)
    if not duel or duel["status"] != "active":
        return

    q_index = duel["turn"]
    if q_index >= len(duel["questions"]):
        await finish_duel(update, context, duel_id)
        return

    duel["question_active"] = True
    duel["correct_answered"] = False
    duel["p1_answered"] = False
    duel["p2_answered"] = False
    duel["waiting_for_answer"] = True

    question = duel["questions"][q_index]
    p1 = duel["player1"]
    p2 = duel["player2"]
    is_bot = duel.get("is_bot", False)

    work = question.get("work", "")
    if not work:
        work = extract_work(question.get("text", ""))
    
    work_text = f"\n📖 *{work}*" if work else ""

    text = (
        f"❓ *Вопрос {q_index + 1} из 5*\n\n"
        f"{question['text']}\n"
        f"{work_text}\n\n"
        f"_Выбери вариант ответа:_"
    )

    keyboard = []
    for idx, option in enumerate(question["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"ans|{duel_id}|{idx}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        p1,
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

    if is_bot and p2 == "bot":
        bot_answer = get_bot_answer(question)
        asyncio.create_task(handle_bot_answer(update, context, duel_id, bot_answer))
    else:
        await context.bot.send_message(
            p2,
            text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


async def handle_bot_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, duel_id: str, bot_answer_idx: int):
    """Обрабатывает ответ бота"""
    await asyncio.sleep(1.5)
    
    duel = duels.get(duel_id)
    if not duel or duel["status"] != "active":
        return
    
    if duel.get("correct_answered", False):
        return
    
    q_index = duel["turn"]
    if q_index >= len(duel["questions"]):
        return
    
    original_question = duel["questions"][q_index]
    is_correct = (bot_answer_idx == original_question["correct"])
    
    duel["p2_answered"] = True
    
    if is_correct:
        duel["p2_score"] += 1
        duel["correct_answered"] = True
        duel["question_active"] = False
        duel["waiting_for_answer"] = False
        
        await context.bot.send_message(
            duel["player1"],
            f"🤖 Бот ответил правильно! +1 очко за бота!"
        )
    else:
        await context.bot.send_message(
            duel["player1"],
            f"🤖 Бот ответил неправильно!"
        )


async def send_correct_answer_and_continue(update: Update, context: ContextTypes.DEFAULT_TYPE, duel_id: str):
    duel = duels.get(duel_id)
    if not duel:
        return

    q_index = duel["turn"]
    if q_index >= len(duel["questions"]):
        await finish_duel(update, context, duel_id)
        return

    question = duel["questions"][q_index]
    correct_idx = question["correct"]
    correct_text = question["options"][correct_idx]

    p1 = duel["player1"]
    p2 = duel["player2"]

    message_text = f"✅ *Правильный ответ:* {correct_text}"

    await context.bot.send_message(p1, message_text, parse_mode="Markdown")
    if p2 != "bot":
        await context.bot.send_message(p2, message_text, parse_mode="Markdown")

    await asyncio.sleep(2)
    duel["turn"] += 1
    await ask_question(update, context, duel_id)


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        print(f"⚠️ Устаревшая кнопка: {e}")
        return
    
    data = query.data
    
    if data.startswith("ans|"):
        parts = data.split("|")
        duel_id = parts[1]
        answer_idx = int(parts[2])

        duel = duels.get(duel_id)
        if not duel or duel["status"] != "active":
            try:
                await query.edit_message_text("❌ Дуэль уже завершена.")
            except Exception:
                pass
            return

        if not duel.get("waiting_for_answer", False):
            try:
                await query.edit_message_text("⏳ Этот вопрос уже завершён!")
            except Exception:
                pass
            return

        if not duel.get("question_active", False):
            try:
                await query.edit_message_text("⏳ Этот вопрос уже завершён!")
            except Exception:
                pass
            return

        if duel.get("correct_answered", False):
            try:
                await query.edit_message_text("⏳ Соперник уже правильно ответил!")
            except Exception:
                pass
            return

        q_index = duel["turn"]
        if q_index >= len(duel["questions"]):
            try:
                await query.edit_message_text("❌ Дуэль уже завершена.")
            except Exception:
                pass
            return

        player_id = update.effective_user.id

        if player_id == duel["player1"]:
            player_id_other = duel["player2"] if duel.get("player2") != "bot" else None
            player_key = "p1"
            opponent_key = "p2"
        else:
            player_id_other = duel["player1"]
            player_key = "p2"
            opponent_key = "p1"

        if duel.get(f"{player_key}_answered", False):
            try:
                await query.edit_message_text("⏳ Ты уже отвечал на этот вопрос!")
            except Exception:
                pass
            return

        duel[f"{player_key}_answered"] = True

        original_question = duel["questions"][q_index]
        correct = original_question["correct"]
        is_correct = (answer_idx == correct)

        if is_correct:
            duel[f"{player_key}_score"] += 1
            duel["correct_answered"] = True
            duel["question_active"] = False
            duel["waiting_for_answer"] = False

            try:
                await query.edit_message_text(f"✅ *Правильно!* +1 очко!", parse_mode="Markdown")
            except Exception:
                pass

            if player_id_other:
                await context.bot.send_message(
                    player_id_other,
                    f"❌ Соперник ответил правильно! Он получает +1 очко."
                )

            await send_correct_answer_and_continue(update, context, duel_id)

        else:
            try:
                await query.edit_message_text("❌ *Неправильно.*", parse_mode="Markdown")
            except Exception:
                pass

            if duel.get("is_bot", False) and duel.get("p2_answered", False):
                duel["question_active"] = False
                duel["waiting_for_answer"] = False
                await send_correct_answer_and_continue(update, context, duel_id)
            elif duel.get(f"{opponent_key}_answered", False):
                duel["question_active"] = False
                duel["waiting_for_answer"] = False
                if player_id_other:
                    await context.bot.send_message(
                        player_id_other,
                        f"⏳ Оба ответили неправильно!"
                    )
                await send_correct_answer_and_continue(update, context, duel_id)
            else:
                if player_id_other:
                    await context.bot.send_message(
                        player_id_other,
                        f"🔔 Соперник ответил неправильно! Твой ход!"
                    )
    
    elif data.startswith("b|"):
        parts = data.split("|")
        duel_id = parts[1]
        player_id = int(parts[2])
        bonus_code = parts[3]

        duel = duels.get(duel_id)
        if not duel:
            try:
                await query.edit_message_text("❌ Дуэль завершена.")
            except Exception:
                pass
            return

        if player_id == duel["player1"]:
            player_key = "p1"
            opponent_id = duel["player2"]
        else:
            player_key = "p2"
            opponent_id = duel["player1"]

        used = duel.setdefault(f"{player_key}_used", [])
        if bonus_code in used:
            try:
                await query.edit_message_text("⚠️ Бонус уже использован.")
            except Exception:
                pass
            return

        used.append(bonus_code)

        if bonus_code == "b1":
            duel[f"{player_key}_score"] += 1
            try:
                await query.edit_message_text("💪 +1 очко за «Уверенность»!")
            except Exception:
                pass
        elif bonus_code == "b2":
            try:
                await query.edit_message_text("🔍 «Подсказка» активирована!")
            except Exception:
                pass
        elif bonus_code == "b3":
            try:
                await query.edit_message_text("🔄 «Пересдача» активирована!")
            except Exception:
                pass
        elif bonus_code == "b4":
            if not duel.get("correct_answered", False) and duel.get("question_active", False):
                duel[f"{player_key}_score"] += 1
                duel["correct_answered"] = True
                duel["question_active"] = False
                duel["waiting_for_answer"] = False
                try:
                    await query.edit_message_text("⭐ «Автопобеда»! Вопрос засчитан как правильный!")
                except Exception:
                    pass

                await context.bot.send_message(
                    opponent_id,
                    f"❌ Соперник использовал «Автопобеду»!"
                )

                await send_correct_answer_and_continue(update, context, duel_id)
            else:
                try:
                    await query.edit_message_text("⚠️ Сейчас нельзя использовать этот бонус!")
                except Exception:
                    pass
        else:
            try:
                await query.edit_message_text(f"🔍 Бонус активирован!")
            except Exception:
                pass

    elif data.startswith("s|"):
        parts = data.split("|")
        duel_id = parts[1]
        player_id = int(parts[2])

        duel = duels.get(duel_id)
        if not duel:
            try:
                await query.edit_message_text("❌ Дуэль завершена.")
            except Exception:
                pass
            return
        if duel["status"] != "active":
            try:
                await query.edit_message_text("❌ Дуэль уже завершена.")
            except Exception:
                pass
            return

        if duel.get("is_bot", False):
            winner = duel["player2"]
            loser = duel["player1"]
            update_duel_stats(winner, True) if isinstance(winner, int) else None
            update_duel_stats(loser, False)
            
            await context.bot.send_message(
                duel["player1"],
                f"🤖 Бот победил! Ты сдался."
            )
        else:
            if player_id == duel["player1"]:
                winner = duel["player2"]
                loser = duel["player1"]
            else:
                winner = duel["player1"]
                loser = duel["player2"]

            update_duel_stats(winner, True)
            update_duel_stats(loser, False)

            await context.bot.send_message(winner, f"🏆 *Победа!* Соперник сдался.", parse_mode="Markdown")
            await context.bot.send_message(loser, f"😔 *Ты сдался.*", parse_mode="Markdown")

        if duel["player1"] in user_duel:
            del user_duel[duel["player1"]]
        if duel["player2"] in user_duel and duel["player2"] != "bot":
            del user_duel[duel["player2"]]
        duels.pop(duel_id, None)

        try:
            await query.edit_message_text("🏳️ Дуэль завершена.")
        except Exception:
            pass


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

    if duel.get("is_bot", False):
        await context.bot.send_message(
            duel["player1"],
            f"🤖 Бот победил! Ты завершил дуэль командой /stopduel."
        )
    else:
        if user_id == duel["player1"]:
            winner = duel["player2"]
            loser = duel["player1"]
        else:
            winner = duel["player1"]
            loser = duel["player2"]

        update_duel_stats(winner, True)
        update_duel_stats(loser, False)

        await context.bot.send_message(
            winner,
            f"🏆 *Ты победил!* Соперник завершил дуэль командой /stopduel.",
            parse_mode="Markdown"
        )
        await context.bot.send_message(
            loser,
            f"😔 *Ты завершил дуэль командой /stopduel.*",
            parse_mode="Markdown"
        )

    if duel["player1"] in user_duel:
        del user_duel[duel["player1"]]
    if duel["player2"] in user_duel and duel["player2"] != "bot":
        del user_duel[duel["player2"]]
    duels.pop(duel_id, None)

    await update.message.reply_text("🏳️ *Дуэль завершена командой /stopduel.*", parse_mode="Markdown")


async def finish_duel(update: Update, context: ContextTypes.DEFAULT_TYPE, duel_id: str):
    duel = duels.get(duel_id)
    if not duel:
        return

    duel["status"] = "finished"
    p1 = duel["player1"]
    p2 = duel["player2"]
    p1_score = duel.get("p1_score", 0)
    p2_score = duel.get("p2_score", 0)
    is_bot = duel.get("is_bot", False)

    if p1_score > p2_score:
        winner, loser = p1, p2
        await context.bot.send_message(winner, f"🏆 *Ты победил!* {p1_score}:{p2_score}", parse_mode="Markdown")
        if not is_bot:
            await context.bot.send_message(loser, f"😔 *Ты проиграл.* {p1_score}:{p2_score}", parse_mode="Markdown")
        update_duel_stats(winner, True)
        if not is_bot:
            update_duel_stats(loser, False)
    elif p2_score > p1_score:
        winner, loser = p2, p1
        if is_bot:
            await context.bot.send_message(p1, f"🤖 *Бот победил!* {p2_score}:{p1_score}", parse_mode="Markdown")
        else:
            await context.bot.send_message(winner, f"🏆 *Ты победил!* {p2_score}:{p1_score}", parse_mode="Markdown")
            await context.bot.send_message(loser, f"😔 *Ты проиграл.* {p2_score}:{p1_score}", parse_mode="Markdown")
        if not is_bot:
            update_duel_stats(winner, True)
            update_duel_stats(loser, False)
    else:
        if is_bot:
            await context.bot.send_message(p1, f"🤝 *Ничья с ботом!* {p1_score}:{p2_score}", parse_mode="Markdown")
        else:
            await context.bot.send_message(p1, f"🤝 *Ничья!* {p1_score}:{p2_score}", parse_mode="Markdown")
            await context.bot.send_message(p2, f"🤝 *Ничья!* {p2_score}:{p1_score}", parse_mode="Markdown")

    if p1 in user_duel:
        del user_duel[p1]
    if p2 in user_duel and p2 != "bot":
        del user_duel[p2]
    if p1 in user_selection:
        del user_selection[p1]
    duels.pop(duel_id, None)


def cancel_duel(duel_id: str):
    duel = duels.pop(duel_id, None)
    if duel:
        for pid in [duel.get("player1"), duel.get("player2")]:
            if pid in user_duel and pid != "bot":
                del user_duel[pid]
            if pid in user_selection:
                del user_selection[pid]