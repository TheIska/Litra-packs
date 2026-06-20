import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection, get_user, update_duel_stats, get_opponent
from ..models.questions import QUESTIONS
from ..utils.helpers import shuffle_question

duels = {}
user_duel = {}
user_selection = {}

BONUSES = {
    "обычный": {"name": "Уверенность", "code": "b1"},
    "редкий": {"name": "Подсказка", "code": "b2"},
    "эпический": {"name": "Пересдача", "code": "b3"},
    "легендарный": {"name": "Автопобеда", "code": "b4"},
}


async def duel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()
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

    user_selection[user_id] = {
        "selected": [],
        "page": 0
    }
    await show_hero_selection(update, context, user_id, chat_id)


async def show_hero_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int):
    """Показывает интерфейс выбора героев с пагинацией по 5 героев"""
    collection = get_collection(user_id)
    hero_keys = list(collection.keys())
    
    if len(hero_keys) <= 3:
        user_selection[user_id]["selected"] = hero_keys.copy()
        await start_duel_after_selection(update, context, user_id)
        return
    
    user_data = user_selection.get(user_id, {"selected": [], "page": 0})
    selected = user_data.get("selected", [])
    page = user_data.get("page", 0)
    
    # Всего страниц
    per_page = 5
    total_pages = (len(hero_keys) + per_page - 1) // per_page
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, len(hero_keys))
    
    keyboard = []
    
    # Показываем героев на текущей странице (по 5)
    for i in range(start_idx, end_idx):
        key = hero_keys[i]
        hero = collection[key]
        is_selected = key in selected
        emoji = "✅" if is_selected else "⬜"
        keyboard.append([InlineKeyboardButton(
            f"{emoji} {hero['name'][:25]}",
            callback_data=f"hsel|{i}"
        )])
    
    # Кнопки навигации
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"hpage|{page-1}"))
    if page < total_pages - 1:
        nav_row.append(InlineKeyboardButton("➡️ Вперед", callback_data=f"hpage|{page+1}"))
    if nav_row:
        keyboard.append(nav_row)
    
    # Информация о странице
    if total_pages > 1:
        keyboard.append([InlineKeyboardButton(
            f"📄 Страница {page+1}/{total_pages}",
            callback_data="noop"
        )])
    
    keyboard.append([InlineKeyboardButton("⚔️ Начать дуэль", callback_data="startduel")])
    keyboard.append([InlineKeyboardButton("🔙 Отмена", callback_data="main_menu")])
    
    selected_count = len(selected)
    
    text = (
        f"⚔️ *Выбор героев для дуэли*\n\n"
        f"Выбери *3 героя*, которые будут участвовать в дуэли.\n"
        f"Выбрано: {selected_count}/3\n\n"
        f"⬜ — не выбран, ✅ — выбран\n"
        f"_Нажми на героя, чтобы выбрать/отменить_"
    )
    
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


async def handle_hero_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор героев"""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data.startswith("hsel|"):
        # Выбор героя
        try:
            hero_idx = int(data.split("|")[1])
        except (IndexError, ValueError):
            await query.answer("❌ Ошибка!", show_alert=True)
            return
        
        collection = get_collection(user_id)
        hero_keys = list(collection.keys())
        if hero_idx >= len(hero_keys):
            await query.answer("❌ Ошибка!", show_alert=True)
            return
        
        hero_key = hero_keys[hero_idx]
        user_data = user_selection.get(user_id, {"selected": [], "page": 0})
        selected = user_data.get("selected", [])
        
        if hero_key in selected:
            selected.remove(hero_key)
        else:
            if len(selected) >= 3:
                await query.answer("❌ Ты уже выбрал 3 героев!", show_alert=True)
                return
            selected.append(hero_key)
        
        user_selection[user_id]["selected"] = selected
        await show_hero_selection(update, context, user_id, query.message.chat_id)
    
    elif data.startswith("hpage|"):
        # Смена страницы
        try:
            page = int(data.split("|")[1])
        except (IndexError, ValueError):
            await query.answer("❌ Ошибка!", show_alert=True)
            return
        
        user_selection[user_id]["page"] = page
        await show_hero_selection(update, context, user_id, query.message.chat_id)
    
    elif data == "startduel":
        user_data = user_selection.get(user_id, {"selected": [], "page": 0})
        selected = user_data.get("selected", [])
        
        if len(selected) != 3:
            await query.answer("❌ Выбери ровно 3 героев!", show_alert=True)
            return
        
        await start_duel_after_selection(update, context, user_id)
    
    elif data == "main_menu":
        user_selection.pop(user_id, None)
        from .start import start
        await start(update, context)


async def start_duel_after_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int):
    """Запускает дуэль после выбора героев"""
    collection = get_collection(user_id)
    user_data = user_selection.get(user_id, {"selected": [], "page": 0})
    selected_heroes = user_data.get("selected", [])
    
    if len(selected_heroes) != 3:
        await show_hero_selection(update, context, user_id, update.effective_chat.id)
        return
    
    opponent_id = get_opponent(user_id)
    if not opponent_id:
        user_selection.pop(user_id, None)
        await context.bot.send_message(user_id, "😴 Нет других игроков. Попробуй позже.")
        return
    
    if opponent_id in user_duel:
        user_selection.pop(user_id, None)
        await context.bot.send_message(user_id, "Соперник уже в игре.")
        return
    
    p2_collection = get_collection(opponent_id)
    p2_keys = list(p2_collection.keys())
    if len(p2_keys) < 3:
        user_selection.pop(user_id, None)
        await context.bot.send_message(user_id, "❌ У соперника меньше 3 героев.")
        return
    
    p2_chosen = random.sample(p2_keys, 3)
    p1_chosen = selected_heroes
    
    user_selection.pop(user_id, None)
    
    duel_id = f"{user_id}_{opponent_id}_{random.randint(1000,9999)}"
    
    duels[duel_id] = {
        "player1": user_id,
        "player2": opponent_id,
        "status": "active",
        "p1_score": 0,
        "p2_score": 0,
        "p1_used": [],
        "p2_used": [],
        "questions": random.sample(QUESTIONS, 5),
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
        f"Твои герои: {', '.join(p1_names)}\n"
        f"Всего вопросов: 5\n\n"
        f"За каждый правильный ответ — 1 очко.",
        parse_mode="Markdown"
    )
    
    await context.bot.send_message(
        opponent_id,
        f"⚔️ Игрок вызвал тебя на дуэль!\n"
        f"Твои герои: {', '.join(p2_names)}\n"
        f"Всего вопросов: 5\n\n"
        f"За каждый правильный ответ — 1 очко.",
        parse_mode="Markdown"
    )
    
    await ask_question(update, context, duel_id)


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

    text = (
        f"❓ *Вопрос {q_index + 1} из 5*\n\n"
        f"{question['text']}\n\n"
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

    await context.bot.send_message(
        p2,
        text,
        parse_mode="Markdown",
        reply_markup=reply_markup
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
    await context.bot.send_message(p2, message_text, parse_mode="Markdown")

    await asyncio.sleep(2)
    duel["turn"] += 1
    await ask_question(update, context, duel_id)


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("ans|"):
        parts = data.split("|")
        duel_id = parts[1]
        answer_idx = int(parts[2])

        duel = duels.get(duel_id)
        if not duel or duel["status"] != "active":
            await query.edit_message_text("❌ Дуэль уже завершена.")
            return

        if not duel.get("waiting_for_answer", False):
            await query.edit_message_text("⏳ Этот вопрос уже завершён!")
            return

        if not duel.get("question_active", False):
            await query.edit_message_text("⏳ Этот вопрос уже завершён!")
            return

        if duel.get("correct_answered", False):
            await query.edit_message_text("⏳ Соперник уже правильно ответил!")
            return

        q_index = duel["turn"]
        if q_index >= len(duel["questions"]):
            await query.edit_message_text("❌ Дуэль уже завершена.")
            return

        player_id = update.effective_user.id

        if player_id == duel["player1"]:
            player_id_other = duel["player2"]
            player_key = "p1"
            opponent_key = "p2"
        else:
            player_id_other = duel["player1"]
            player_key = "p2"
            opponent_key = "p1"

        if duel.get(f"{player_key}_answered", False):
            await query.edit_message_text("⏳ Ты уже отвечал на этот вопрос!")
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

            await query.edit_message_text(f"✅ *Правильно!* +1 очко!", parse_mode="Markdown")

            await context.bot.send_message(
                player_id_other,
                f"❌ Соперник ответил правильно! Ты не получаешь очко."
            )

            await send_correct_answer_and_continue(update, context, duel_id)

        else:
            await query.edit_message_text("❌ *Неправильно.*", parse_mode="Markdown")

            if duel.get(f"{opponent_key}_answered", False):
                duel["question_active"] = False
                duel["waiting_for_answer"] = False
                await context.bot.send_message(
                    player_id_other,
                    f"⏳ Оба ответили неправильно!"
                )
                await send_correct_answer_and_continue(update, context, duel_id)
            else:
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
            await query.edit_message_text("❌ Дуэль завершена.")
            return

        if player_id == duel["player1"]:
            player_key = "p1"
            opponent_id = duel["player2"]
        else:
            player_key = "p2"
            opponent_id = duel["player1"]

        used = duel.setdefault(f"{player_key}_used", [])
        if bonus_code in used:
            await query.edit_message_text("⚠️ Бонус уже использован.")
            return

        used.append(bonus_code)

        if bonus_code == "b1":
            duel[f"{player_key}_score"] += 1
            await query.edit_message_text("💪 +1 очко за «Уверенность»!")
        elif bonus_code == "b2":
            await query.edit_message_text("🔍 «Подсказка» активирована!")
        elif bonus_code == "b3":
            await query.edit_message_text("🔄 «Пересдача» активирована!")
        elif bonus_code == "b4":
            if not duel.get("correct_answered", False) and duel.get("question_active", False):
                duel[f"{player_key}_score"] += 1
                duel["correct_answered"] = True
                duel["question_active"] = False
                duel["waiting_for_answer"] = False
                await query.edit_message_text("⭐ «Автопобеда»! Вопрос засчитан как правильный!")

                await context.bot.send_message(
                    opponent_id,
                    f"❌ Соперник использовал «Автопобеду»!"
                )

                await send_correct_answer_and_continue(update, context, duel_id)
            else:
                await query.edit_message_text("⚠️ Сейчас нельзя использовать этот бонус!")
        else:
            await query.edit_message_text(f"🔍 Бонус активирован!")

    elif data.startswith("s|"):
        parts = data.split("|")
        duel_id = parts[1]
        player_id = int(parts[2])

        duel = duels.get(duel_id)
        if not duel:
            await query.edit_message_text("❌ Дуэль завершена.")
            return
        if duel["status"] != "active":
            await query.edit_message_text("❌ Дуэль уже завершена.")
            return

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
        if duel["player2"] in user_duel:
            del user_duel[duel["player2"]]
        duels.pop(duel_id, None)

        await query.edit_message_text("🏳️ Дуэль завершена.")


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
    if duel["player2"] in user_duel:
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

    if p1_score > p2_score:
        winner, loser = p1, p2
        await context.bot.send_message(winner, f"🏆 *Ты победил!* {p1_score}:{p2_score}", parse_mode="Markdown")
        await context.bot.send_message(loser, f"😔 *Ты проиграл.* {p1_score}:{p2_score}", parse_mode="Markdown")
        update_duel_stats(winner, True)
        update_duel_stats(loser, False)
    elif p2_score > p1_score:
        winner, loser = p2, p1
        await context.bot.send_message(winner, f"🏆 *Ты победил!* {p2_score}:{p1_score}", parse_mode="Markdown")
        await context.bot.send_message(loser, f"😔 *Ты проиграл.* {p2_score}:{p1_score}", parse_mode="Markdown")
        update_duel_stats(winner, True)
        update_duel_stats(loser, False)
    else:
        await context.bot.send_message(p1, f"🤝 *Ничья!* {p1_score}:{p2_score}", parse_mode="Markdown")
        await context.bot.send_message(p2, f"🤝 *Ничья!* {p2_score}:{p1_score}", parse_mode="Markdown")

    if p1 in user_duel:
        del user_duel[p1]
    if p2 in user_duel:
        del user_duel[p2]
    duels.pop(duel_id, None)


def cancel_duel(duel_id: str):
    duel = duels.pop(duel_id, None)
    if duel:
        for pid in [duel.get("player1"), duel.get("player2")]:
            if pid in user_duel:
                del user_duel[pid]