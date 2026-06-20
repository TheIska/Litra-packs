import random
import asyncio
import hashlib
import time
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection, get_user, update_duel_stats, get_opponent, get_all_users
from ..models.questions import QUESTIONS
from ..utils.helpers import shuffle_question, extract_work

duels = {}
user_duel = {}
user_selection = {}
invite_codes = {}
searching_players = set()  # Игроки, которые ищут случайного соперника

BONUSES = {
    "обычный": {"name": "Уверенность", "code": "b1"},
    "редкий": {"name": "Подсказка", "code": "b2"},
    "эпический": {"name": "Пересдача", "code": "b3"},
    "легендарный": {"name": "Автопобеда", "code": "b4"},
}

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


def generate_invite_code(user_id: int) -> str:
    raw = f"{user_id}_{time.time()}_{random.randint(1000,9999)}"
    code = hashlib.md5(raw.encode()).hexdigest()[:8].upper()
    invite_codes[code] = {"inviter": user_id, "created_at": time.time()}
    return code


def get_bot_name() -> str:
    return "LiteraPacksBot"


def get_weighted_questions(selected_heroes, collection, all_questions, count=5):
    """Выбирает вопросы с учётом бонусов от выбранных героев"""
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


async def show_menu(update, context, user_id, chat_id, text, keyboard):
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        if "Message is not modified" not in str(e):
            print(f"⚠️ Ошибка: {e}")


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
        [InlineKeyboardButton("🎲 Случайный соперник", callback_data="duel_random")],
        [InlineKeyboardButton("👤 С другом из списка", callback_data="duel_friend")],
        [InlineKeyboardButton("🔗 Пригласить друга по ссылке", callback_data="duel_invite")],
        [InlineKeyboardButton("🤖 С ботом", callback_data="duel_bot")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    text = "⚔️ *Выбери тип дуэли*\n\n🎲 *Случайный соперник* — найди случайного игрока\n👤 *С другом из списка* — выбери друга из списка\n🔗 *Пригласить друга по ссылке* — получи ссылку для друга\n🤖 *С ботом* — сражайся против ИИ\n\nДля дуэли нужно *3 героя* в коллекции."
    await show_menu(update, context, user_id, chat_id, text, InlineKeyboardMarkup(keyboard))


async def duel_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    collection = get_collection(user_id)
    if len(collection) < 3:
        await query.edit_message_text("❌ У тебя меньше 3 героев. Открой паки!")
        return

    code = generate_invite_code(user_id)
    invite_link = f"https://t.me/{get_bot_name()}?start=duel_{code}"

    keyboard = [
        [InlineKeyboardButton("📋 Скопировать ссылку", callback_data=f"copy_link|{invite_link}")],
        [InlineKeyboardButton("📤 Поделиться", callback_data=f"share_link|{invite_link}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="duel")],
    ]
    text = f"🔗 *Пригласи друга на дуэль!*\n\nОтправь другу ссылку:\n`{invite_link}`\n\n⚠️ Ссылка действует *5 минут*"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def copy_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    link = query.data.split("|")[1]
    await query.edit_message_text(f"🔗 Ссылка скопирована! Отправь другу:\n\n`{link}`\n\n⚠️ Ссылка действует 5 минут.", parse_mode="Markdown")


async def share_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    link = query.data.split("|")[1]
    keyboard = [
        [InlineKeyboardButton("📋 Скопировать ссылку", callback_data=f"copy_link|{link}")],
        [InlineKeyboardButton("🔙 Назад", callback_data="duel")],
    ]
    text = f"🔗 *Поделись ссылкой с другом:*\n\n`{link}`\n\nИли отправь текст:\n*Привет! Давай сразимся в дуэли в боте «Литературный Герой»!*\nПерейди по ссылке: {link}\n\n⚠️ Ссылка действует 5 минут."
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_invite_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].startswith("duel_"):
        return

    code = context.args[0].replace("duel_", "")
    user_id = update.effective_user.id
    invite = invite_codes.get(code)

    if not invite or time.time() - invite["created_at"] > 300:
        await update.message.reply_text("❌ Ссылка недействительна или истекла (5 минут).")
        return

    inviter_id = invite["inviter"]
    if user_id == inviter_id:
        await update.message.reply_text("❌ Нельзя пригласить самого себя!")
        return

    if inviter_id in user_duel:
        await update.message.reply_text("❌ Игрок уже в дуэли.")
        return

    if len(get_collection(inviter_id)) < 3 or len(get_collection(user_id)) < 3:
        await update.message.reply_text("❌ У одного из игроков меньше 3 героев.")
        return

    invite_codes.pop(code, None)
    await proceed_to_hero_selection(update, context, user_id, update.effective_chat.id, inviter_id, True)


async def duel_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    users = [u for u in get_all_users() if u["user_id"] != user_id]
    if not users:
        await query.edit_message_text("😴 Нет других игроков. Попробуй позже.")
        return

    keyboard = []
    for user in users[:20]:
        try:
            chat = await context.bot.get_chat(user["user_id"])
            name = chat.first_name or f"ID: {user['user_id']}"
        except:
            name = f"ID: {user['user_id']}"
        hero_count = len(get_collection(user["user_id"]))
        keyboard.append([InlineKeyboardButton(f"👤 {name} ({hero_count} героев)", callback_data=f"duel_friend_select|{user['user_id']}")])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="duel")])
    await query.edit_message_text("👤 *Выбери друга для дуэли:*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


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
    await context.bot.send_message(friend_id, f"⚔️ *{update.effective_user.first_name} хочет вызвать тебя на дуэль!*", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
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

    await proceed_to_hero_selection(update, context, user_id, query.message.chat_id, opponent_id, False)


async def duel_decline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Ты отказался от дуэли.")


async def duel_random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает поиск случайного соперника"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    # Проверяем, есть ли уже игрок в очереди поиска
    if user_id in searching_players:
        await context.bot.send_message(chat_id, "⏳ Ты уже в поиске соперника...")
        return

    if user_id in user_duel:
        await context.bot.send_message(chat_id, "⚠️ У тебя уже есть активная дуэль!")
        return

    # Добавляем игрока в очередь поиска
    searching_players.add(user_id)
    await context.bot.send_message(chat_id, "🔍 *Поиск случайного соперника...*\n\n_Ожидай, скоро найдётся!_", parse_mode="Markdown")

    # Ищем соперника среди других игроков в очереди
    opponent_id = None
    for pid in list(searching_players):
        if pid != user_id:
            opponent_id = pid
            break

    if opponent_id:
        # Удаляем обоих из очереди
        searching_players.discard(user_id)
        searching_players.discard(opponent_id)
        
        # Проверяем, что соперник не в дуэли
        if opponent_id in user_duel:
            searching_players.add(user_id)
            await context.bot.send_message(chat_id, "❌ Соперник уже начал дуэль. Попробуй ещё раз.")
            return

        # Проверяем коллекцию соперника
        if len(get_collection(opponent_id)) < 3:
            searching_players.add(user_id)
            await context.bot.send_message(chat_id, "❌ У соперника меньше 3 героев. Ищем другого...")
            # Продолжаем поиск
            await duel_random(update, context)
            return

        # Запускаем дуэль
        await proceed_to_hero_selection(update, context, user_id, chat_id, opponent_id, random_match=True)
    else:
        # Ждём 30 секунд, если никто не нашёлся
        await asyncio.sleep(30)
        
        # Проверяем, не добавился ли кто-то за это время
        opponent_id = None
        for pid in list(searching_players):
            if pid != user_id:
                opponent_id = pid
                break

        if opponent_id:
            searching_players.discard(user_id)
            searching_players.discard(opponent_id)
            if len(get_collection(opponent_id)) < 3:
                searching_players.add(user_id)
                await context.bot.send_message(chat_id, "❌ У соперника меньше 3 героев. Попробуй позже.")
                return
            await proceed_to_hero_selection(update, context, user_id, chat_id, opponent_id, random_match=True)
        else:
            searching_players.discard(user_id)
            await context.bot.send_message(chat_id, "😴 *Никто не нашёлся за 30 секунд.*\nПопробуй ещё раз или выбери другой режим!", parse_mode="Markdown")


async def duel_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    chat_id = query.message.chat_id

    if len(get_collection(user_id)) < 3:
        await context.bot.send_message(chat_id, "❌ У тебя меньше 3 героев. Открой паки!")
        return
    await show_hero_selection_for_duel(update, context, user_id, chat_id, "bot")


async def proceed_to_hero_selection(update, context, user_id, chat_id, opponent_id, invited=False, random_match=False):
    user_selection[user_id] = {"selected": [], "page": 0, "duel_type": "random" if random_match else "friend", "opponent": opponent_id}
    if invited:
        await context.bot.send_message(opponent_id, "✅ Твой друг принял приглашение на дуэль! Выбирайте героев...")
    await show_hero_selection_for_duel(update, context, user_id, chat_id, "random" if random_match else "friend")


async def show_hero_selection_for_duel(update, context, user_id, chat_id, duel_type):
    collection = get_collection(user_id)
    hero_keys = list(collection.keys())

    if user_id not in user_selection:
        user_selection[user_id] = {"selected": [], "page": 0, "duel_type": duel_type}

    data = user_selection[user_id]
    selected = data["selected"]
    page = data["page"]

    if len(hero_keys) <= 3:
        user_selection[user_id]["selected"] = hero_keys.copy()
        await start_duel_after_selection(update, context, user_id)
        return

    per_page = 5
    total_pages = (len(hero_keys) + per_page - 1) // per_page
    start = page * per_page
    end = min(start + per_page, len(hero_keys))

    keyboard = []
    for i in range(start, end):
        hero = collection[hero_keys[i]]
        rarity = hero.get("rarity", "обычный")
        is_selected = hero_keys[i] in selected
        emoji = "✅" if is_selected else "⬜"
        save_chance = SAVE_CHANCES.get(rarity, 0)
        r_emoji = {"легендарный": "👑", "эпический": "⭐", "редкий": "🔵", "обычный": "📘"}.get(rarity, "📘")
        # Показываем множитель для произведения
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
    
    # Показываем бонусы к произведениям
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

    await show_menu(update, context, user_id, chat_id, text, InlineKeyboardMarkup(keyboard))


async def handle_hero_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        return

    data = query.data
    user_id = query.from_user.id
    chat_id = query.message.chat_id

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
        await show_hero_selection_for_duel(update, context, user_id, chat_id, user_data.get("duel_type", "random"))

    elif data.startswith("hpage|"):
        page = int(data.split("|")[1])
        user_selection[user_id]["page"] = page
        await show_hero_selection_for_duel(update, context, user_id, chat_id, user_selection[user_id].get("duel_type", "random"))

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
    duel_type = data.get("duel_type", "random")
    opponent_id = data.get("opponent")

    if len(selected) != 3:
        return

    if duel_type == "bot":
        await start_bot_duel(update, context, user_id, selected)
        return

    if opponent_id:
        p2_collection = get_collection(opponent_id)
        p2_keys = list(p2_collection.keys())
        rarity_order = {"легендарный": 0, "эпический": 1, "редкий": 2, "обычный": 3}
        sorted_keys = sorted(p2_keys, key=lambda k: rarity_order.get(p2_collection[k].get("rarity", "обычный"), 4))
        p2_chosen = sorted_keys[:3] if len(sorted_keys) >= 3 else random.sample(p2_keys, 3)
        await start_duel(update, context, user_id, opponent_id, selected, p2_chosen)
        return

    # Если соперник не найден (ошибка)
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
        "p1_score": 0, "p2_score": 0, "p1_used": [], "p2_used": [],
        "questions": questions, "turn": 0,
        "p1_chosen": p1_chosen, "p2_chosen": p2_chosen,
        "question_active": False, "correct_answered": False,
        "p1_answered": False, "p2_answered": False,
        "waiting_for_answer": False, "is_bot": False,
        "p1_save_chance": p1_save, "p2_save_chance": p2_save,
        "p1_save_used": False, "p2_save_used": False,
    }

    user_duel[user_id] = duel_id
    user_duel[opponent_id] = duel_id

    p1_names = [collection[k]['name'] for k in p1_chosen]
    p2_names = [p2_collection[k]['name'] for k in p2_chosen]

    await context.bot.send_message(user_id, f"⚔️ *Дуэль началась!*\nТвои герои: {', '.join(p1_names)}\n🔄 Шанс спасения: {p1_save}%\n\nВсего вопросов: 5\nЗа каждый правильный ответ — 1 очко.", parse_mode="Markdown")
    await context.bot.send_message(opponent_id, f"⚔️ *Дуэль началась!*\nТвои герои: {', '.join(p2_names)}\n🔄 Шанс спасения: {p2_save}%\n\nВсего вопросов: 5\nЗа каждый правильный ответ — 1 очко.", parse_mode="Markdown")

    user_selection.pop(user_id, None)
    await ask_question(update, context, duel_id)


async def start_bot_duel(update, context, user_id, p1_chosen):
    collection = get_collection(user_id)
    from ..models.hero import HEROES
    bot_heroes = random.sample(HEROES, 3)

    questions = get_weighted_questions(p1_chosen, collection, QUESTIONS, 5)
    p1_save = get_save_chance(p1_chosen, collection)

    duel_id = f"{user_id}_bot_{random.randint(1000,9999)}"
    duels[duel_id] = {
        "player1": user_id, "player2": "bot", "status": "active",
        "p1_score": 0, "p2_score": 0, "p1_used": [], "p2_used": [],
        "questions": questions, "turn": 0,
        "p1_chosen": p1_chosen, "p2_chosen": [h['name'] for h in bot_heroes],
        "question_active": False, "correct_answered": False,
        "p1_answered": False, "p2_answered": False,
        "waiting_for_answer": False, "is_bot": True, "bot_heroes": bot_heroes,
        "p1_save_chance": p1_save, "p2_save_chance": 0,
        "p1_save_used": False, "p2_save_used": False,
    }

    user_duel[user_id] = duel_id
    p1_names = [collection[k]['name'] for k in p1_chosen]
    p2_names = [h['name'] for h in bot_heroes]

    await context.bot.send_message(user_id,
        f"🤖 *Дуэль с ботом началась!*\nТвои герои: {', '.join(p1_names)}\nГерои бота: {', '.join(p2_names)}\n🔄 Шанс спасения: {p1_save}%\n\n✅ Правильно → +1 очко тебе\n❌ Неправильно → +1 очко боту",
        parse_mode="Markdown")

    user_selection.pop(user_id, None)
    await ask_question(update, context, duel_id)


def get_bot_answer(question):
    return question["correct"] if random.random() < 0.7 else random.choice([i for i in range(len(question["options"])) if i != question["correct"]])


async def ask_question(update, context, duel_id):
    duel = duels.get(duel_id)
    if not duel or duel["status"] != "active":
        return

    if duel["turn"] >= len(duel["questions"]):
        await finish_duel(update, context, duel_id)
        return

    q = duel["questions"][duel["turn"]]
    duel["question_active"] = True
    duel["correct_answered"] = False
    duel["p1_answered"] = False
    duel["p2_answered"] = False
    duel["waiting_for_answer"] = True

    work = q.get("work", extract_work(q.get("text", "")))
    work_text = f"\n📖 *{work}*" if work else ""

    keyboard = [[InlineKeyboardButton(opt, callback_data=f"ans|{duel_id}|{i}")] for i, opt in enumerate(q["options"])]
    text = f"❓ *Вопрос {duel['turn'] + 1} из 5*\n\n{q['text']}{work_text}\n\n_Выбери вариант ответа:_"

    await context.bot.send_message(duel["player1"], text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    if not duel.get("is_bot"):
        await context.bot.send_message(duel["player2"], text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        return

    data = query.data
    if not data.startswith("ans|"):
        return

    _, duel_id, answer_idx = data.split("|")
    answer_idx = int(answer_idx)
    duel = duels.get(duel_id)
    if not duel or duel["status"] != "active":
        return

    if not duel.get("waiting_for_answer") or not duel.get("question_active") or duel.get("correct_answered"):
        await query.edit_message_text("⏳ Этот вопрос уже завершён!")
        return

    if duel["turn"] >= len(duel["questions"]):
        await query.edit_message_text("❌ Дуэль уже завершена.")
        return

    player_id = update.effective_user.id
    is_p1 = player_id == duel["player1"]
    player_key = "p1" if is_p1 else "p2"
    opponent_key = "p2" if is_p1 else "p1"
    
    if duel.get("is_bot"):
        player_other = "bot" if not is_p1 else None
    else:
        player_other = duel.get("player2") if is_p1 else duel.get("player1")
    
    is_bot = duel.get("is_bot", False)

    if duel.get(f"{player_key}_answered"):
        await query.edit_message_text("⏳ Ты уже отвечал на этот вопрос!")
        return

    duel[f"{player_key}_answered"] = True
    q = duel["questions"][duel["turn"]]
    is_correct = answer_idx == q["correct"]

    if is_correct:
        duel[f"{player_key}_score"] += 1
        duel["correct_answered"] = True
        duel["question_active"] = False
        duel["waiting_for_answer"] = False
        await query.edit_message_text("✅ *Правильно!* +1 очко!", parse_mode="Markdown")
        if not is_bot and player_other and player_other != "bot":
            await context.bot.send_message(player_other, "❌ Соперник ответил правильно! Он получает +1 очко.")
        await send_correct_answer_and_continue(update, context, duel_id)
    else:
        save_chance = duel.get(f"{player_key}_save_chance", 0)
        save_used = duel.get(f"{player_key}_save_used", False)

        if not save_used and save_chance > 0 and random.random() * 100 < save_chance:
            duel[f"{player_key}_score"] += 1
            duel["correct_answered"] = True
            duel["question_active"] = False
            duel["waiting_for_answer"] = False
            duel[f"{player_key}_save_used"] = True
            await query.edit_message_text(f"🔄 *Спасение!*\nОтвет был неправильным, но герои спасли тебя! +1 очко! (шанс {save_chance}%)", parse_mode="Markdown")
            if not is_bot and player_other and player_other != "bot":
                await context.bot.send_message(player_other, "🔄 Соперник ошибся, но герои спасли его! Он получает +1 очко.")
            await send_correct_answer_and_continue(update, context, duel_id)
            return

        await query.edit_message_text("❌ *Неправильно.*", parse_mode="Markdown")

        if is_bot:
            duel["p2_score"] += 1
            duel["correct_answered"] = True
            duel["question_active"] = False
            duel["waiting_for_answer"] = False
            await context.bot.send_message(duel["player1"], "🤖 Бот получает +1 очко за твой неправильный ответ!")
            await send_correct_answer_and_continue(update, context, duel_id)
        elif duel.get(f"{opponent_key}_answered"):
            duel["question_active"] = False
            duel["waiting_for_answer"] = False
            if player_other and player_other != "bot":
                await context.bot.send_message(player_other, "⏳ Оба ответили неправильно!")
            await send_correct_answer_and_continue(update, context, duel_id)
        else:
            if player_other and player_other != "bot":
                await context.bot.send_message(player_other, "🔔 Соперник ответил неправильно! Твой ход!")


async def send_correct_answer_and_continue(update, context, duel_id):
    duel = duels.get(duel_id)
    if not duel:
        return

    if duel["turn"] >= len(duel["questions"]):
        await finish_duel(update, context, duel_id)
        return

    q = duel["questions"][duel["turn"]]
    correct_text = q["options"][q["correct"]]
    await context.bot.send_message(duel["player1"], f"✅ *Правильный ответ:* {correct_text}", parse_mode="Markdown")
    if duel["player2"] != "bot":
        await context.bot.send_message(duel["player2"], f"✅ *Правильный ответ:* {correct_text}", parse_mode="Markdown")

    await asyncio.sleep(2)
    duel["turn"] += 1
    await ask_question(update, context, duel_id)


async def finish_duel(update, context, duel_id):
    duel = duels.get(duel_id)
    if not duel:
        return

    duel["status"] = "finished"
    p1, p2 = duel["player1"], duel["player2"]
    p1_score, p2_score = duel["p1_score"], duel["p2_score"]
    is_bot = duel.get("is_bot", False)

    if p1_score > p2_score:
        await context.bot.send_message(p1, f"🏆 *Ты победил!* {p1_score}:{p2_score}", parse_mode="Markdown")
        if not is_bot:
            await context.bot.send_message(p2, f"😔 *Ты проиграл.* {p1_score}:{p2_score}", parse_mode="Markdown")
        update_duel_stats(p1, True)
        if not is_bot:
            update_duel_stats(p2, False)
    elif p2_score > p1_score:
        if is_bot:
            await context.bot.send_message(p1, f"🤖 *Бот победил!* {p2_score}:{p1_score}", parse_mode="Markdown")
        else:
            await context.bot.send_message(p2, f"🏆 *Ты победил!* {p2_score}:{p1_score}", parse_mode="Markdown")
            await context.bot.send_message(p1, f"😔 *Ты проиграл.* {p2_score}:{p1_score}", parse_mode="Markdown")
            update_duel_stats(p2, True)
            update_duel_stats(p1, False)
    else:
        if is_bot:
            await context.bot.send_message(p1, f"🤝 *Ничья с ботом!* {p1_score}:{p2_score}", parse_mode="Markdown")
        else:
            await context.bot.send_message(p1, f"🤝 *Ничья!* {p1_score}:{p2_score}", parse_mode="Markdown")
            await context.bot.send_message(p2, f"🤝 *Ничья!* {p2_score}:{p1_score}", parse_mode="Markdown")

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

    # Удаляем из очереди поиска, если там был
    searching_players.discard(user_id)

    if duel.get("is_bot"):
        await context.bot.send_message(duel["player1"], "🤖 Бот победил! Ты завершил дуэль командой /stopduel.")
    else:
        winner = duel["player2"] if user_id == duel["player1"] else duel["player1"]
        loser = duel["player1"] if user_id == duel["player1"] else duel["player2"]
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
            searching_players.discard(pid)