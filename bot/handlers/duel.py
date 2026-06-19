import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection, get_user, update_duel_stats, get_opponent
from ..models.questions import QUESTIONS
from ..utils.helpers import shuffle_question

duels = {}
user_duel = {}

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
        send_message = query.edit_message_text
    else:
        user_id = update.effective_user.id
        send_message = update.message.reply_text

    if user_id in user_duel:
        await send_message("⚠️ У тебя уже есть активная дуэль! Используй /stopduel.")
        return

    collection = get_collection(user_id)
    if len(collection) < 3:
        await send_message("❌ У тебя меньше 3 героев. Открой паки!")
        return

    opponent_id = get_opponent(user_id)
    if not opponent_id:
        await send_message("😴 Нет других игроков. Попробуй позже.")
        return

    if opponent_id in user_duel:
        await send_message("Соперник уже в игре.")
        return

    hero_keys = list(collection.keys())
    if len(hero_keys) < 3:
        await send_message("❌ У тебя меньше 3 героев.")
        return

    p1_chosen = random.sample(hero_keys, 3)
    p2_collection = get_collection(opponent_id)
    p2_keys = list(p2_collection.keys())
    if len(p2_keys) < 3:
        await send_message("❌ У соперника меньше 3 героев.")
        return
    p2_chosen = random.sample(p2_keys, 3)

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
        "waiting_for_answer": False,  # <--- ДОБАВЛЕНО
    }

    user_duel[user_id] = duel_id
    user_duel[opponent_id] = duel_id

    await send_message(
        f"⚔️ *Дуэль началась!*\n"
        f"Твои герои: {', '.join([collection[k]['name'] for k in p1_chosen])}\n"
        f"Всего вопросов: 5",
        parse_mode="Markdown"
    )

    await context.bot.send_message(
        opponent_id,
        f"⚔️ *{update.effective_user.first_name} вызвал тебя на дуэль!*\n"
        f"Твои герои: {', '.join([p2_collection[k]['name'] for k in p2_chosen])}\n"
        f"Всего вопросов: 5",
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
    duel["waiting_for_answer"] = True  # <--- ДОБАВЛЕНО

    question = shuffle_question(duel["questions"][q_index])
    p1 = duel["player1"]
    p2 = duel["player2"]

    text = f"❓ *Вопрос {q_index+1} из 5*\n\n{question['text']}"

    keyboard = []
    for idx, option in enumerate(question["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"a|{duel_id}|{idx}")])

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


async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split("|")
    action = parts[0]

    if action == "a":
        duel_id = parts[1]
        answer_idx = int(parts[2])

        duel = duels.get(duel_id)
        if not duel or duel["status"] != "active":
            await query.edit_message_text("❌ Дуэль уже завершена.")
            return

        # <--- ДОБАВЛЕНА ПРОВЕРКА
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
        player_key = "p1" if player_id == duel["player1"] else "p2"
        opponent_key = "p2" if player_id == duel["player1"] else "p1"

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
            duel["waiting_for_answer"] = False  # <--- ДОБАВЛЕНО

            await query.edit_message_text(f"✅ *Правильно!* +1 очко!", parse_mode="Markdown")

            await context.bot.send_message(
                duel[opponent_key],
                f"❌ Соперник ответил правильно! Ты не получаешь очко."
            )

            # <--- ПЕРЕХОД К СЛЕДУЮЩЕМУ ВОПРОСУ
            await asyncio.sleep(1.5)
            duel["turn"] += 1
            await ask_question(update, context, duel_id)

        else:
            await query.edit_message_text("❌ *Неправильно.*", parse_mode="Markdown")

            # Проверяем, ответил ли уже соперник
            if duel.get(f"{opponent_key}_answered", False):
                # Оба ответили неправильно
                duel["question_active"] = False
                duel["waiting_for_answer"] = False  # <--- ДОБАВЛЕНО
                await context.bot.send_message(
                    duel[opponent_key],
                    f"⏳ Оба ответили неправильно! Переходим к следующему вопросу."
                )
                await asyncio.sleep(1.5)
                duel["turn"] += 1
                await ask_question(update, context, duel_id)
            else:
                # Ждём ответ соперника
                await context.bot.send_message(
                    duel[opponent_key],
                    f"🔔 Соперник ответил неправильно! Твой ход!"
                )
                # <--- ВАЖНО: НЕ ПЕРЕХОДИМ К СЛЕДУЮЩЕМУ ВОПРОСУ,
                # ЖДЁМ ОТВЕТА ВТОРОГО ИГРОКА

    elif action == "b":
        duel_id = parts[1]
        player_id = int(parts[2])
        bonus_code = parts[3]

        duel = duels.get(duel_id)
        if not duel:
            await query.edit_message_text("❌ Дуэль завершена.")
            return

        player_key = "p1" if player_id == duel["player1"] else "p2"
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
                duel["waiting_for_answer"] = False  # <--- ДОБАВЛЕНО
                await query.edit_message_text("⭐ «Автопобеда»! Вопрос засчитан как правильный!")

                opponent_key = "p2" if player_id == duel["player1"] else "p1"
                await context.bot.send_message(
                    duel[opponent_key],
                    f"❌ Соперник использовал «Автопобеду»!"
                )

                await asyncio.sleep(1.5)
                duel["turn"] += 1
                await ask_question(update, context, duel_id)
            else:
                await query.edit_message_text("⚠️ Сейчас нельзя использовать этот бонус!")
        else:
            await query.edit_message_text(f"🔍 Бонус активирован!")

    elif action == "s":
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