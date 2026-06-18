import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection, get_user, update_duel_stats, get_opponent
from ..models.questions import QUESTIONS

duels = {}
user_duel = {}

BONUSES = {
    "обычный": {"name": "Уверенность", "code": "bonus_1"},
    "редкий": {"name": "Подсказка", "code": "bonus_2"},
    "эпический": {"name": "Пересдача", "code": "bonus_3"},
    "легендарный": {"name": "Автопобеда", "code": "bonus_4"},
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
        await send_message("❌ У тебя меньше 3 героев. Открой паки!")
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
        "questions": random.sample(QUESTIONS, 3),
        "turn": 0,
        "current_player": user_id,
        "p1_chosen": p1_chosen,
        "p2_chosen": p2_chosen,
    }

    user_duel[user_id] = duel_id
    user_duel[opponent_id] = duel_id

    await send_message(
        f"⚔️ *Дуэль началась!*\n"
        f"Твои герои: {', '.join([collection[k]['name'] for k in p1_chosen])}\n"
        f"Первый вопрос для тебя!",
        parse_mode="Markdown"
    )

    await context.bot.send_message(
        opponent_id,
        f"⚔️ *{update.effective_user.first_name} вызвал тебя на дуэль!*\n"
        f"Твои герои: {', '.join([p2_collection[k]['name'] for k in p2_chosen])}\n"
        f"Ожидай своего хода.",
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

    question = duel["questions"][q_index]
    current_player = duel["current_player"]
    player_key = "p1" if current_player == duel["player1"] else "p2"

    text = f"❓ *Вопрос {q_index+1} из {len(duel['questions'])}*\n\n{question['text']}"

    keyboard = []
    for idx, option in enumerate(question["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"ans_{duel_id}_{current_player}_{idx}")])

    hero_keys = duel["p1_chosen"] if current_player == duel["player1"] else duel["p2_chosen"]
    used = duel.get(f"{player_key}_used", [])
    coll = get_collection(current_player)
    bonus_buttons = []
    for hero_key in hero_keys:
        if hero_key in coll:
            hero = coll[hero_key]
            rarity = hero.get("rarity", "обычный")
            bonus = BONUSES.get(rarity, BONUSES["обычный"])
            if bonus["code"] not in used:
                # Используем другой разделитель для бонусов, чтобы избежать конфликта с _
                bonus_buttons.append(InlineKeyboardButton(
                    f"💡 {bonus['name']} ({hero['name']})",
                    callback_data=f"bon|{duel_id}|{current_player}|{bonus['code']}"
                ))

    if bonus_buttons:
        keyboard.append(bonus_buttons)

    keyboard.append([InlineKeyboardButton("🏳️ Сдаться", callback_data=f"sur|{duel_id}|{current_player}")])

    await context.bot.send_message(
        current_player,
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    opponent = duel["player2"] if current_player == duel["player1"] else duel["player1"]
    await context.bot.send_message(
        opponent,
        f"⏳ Ход соперника. Вопрос {q_index+1}."
    )

async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split("|")
    action = parts[0]

    if action == "ans":
        # ans_duel_id_player_id_answer_idx
        _, duel_id, player_id, answer_idx = parts
        player_id = int(player_id)
        answer_idx = int(answer_idx)
        duel = duels.get(duel_id)
        if not duel or duel["status"] != "active" or duel["current_player"] != player_id:
            await query.edit_message_text("⏳ Не твой ход.")
            return

        q_index = duel["turn"]
        question = duel["questions"][q_index]
        correct = question["correct"]
        is_correct = (answer_idx == correct)
        player_key = "p1" if player_id == duel["player1"] else "p2"

        if is_correct:
            duel[f"{player_key}_score"] += 1
            await query.edit_message_text("✅ *Правильно!* +1 очко.", parse_mode="Markdown")
        else:
            used = duel.get(f"{player_key}_used", [])
            if "bonus_3" in used:
                await query.edit_message_text("❌ Неправильно! Есть «Пересдача»! Попробуй ещё раз.")
                await ask_question(update, context, duel_id)
                return
            else:
                await query.edit_message_text("❌ *Неправильно.*", parse_mode="Markdown")

        duel["turn"] += 1
        if duel["current_player"] == duel["player1"]:
            duel["current_player"] = duel["player2"]
        else:
            duel["current_player"] = duel["player1"]

        await asyncio.sleep(0.5)
        await ask_question(update, context, duel_id)

    elif action == "bon":
        # bon|duel_id|player_id|bonus_code
        _, duel_id, player_id, bonus_code = parts
        player_id = int(player_id)
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

        if bonus_code == "bonus_1":
            duel[f"{player_key}_score"] += 1
            await query.edit_message_text("💪 +1 очко за «Уверенность»!")
        elif bonus_code == "bonus_2":
            await query.edit_message_text("🔍 «Подсказка» активирована!")
        elif bonus_code == "bonus_3":
            await query.edit_message_text("🔄 «Пересдача» активирована!")
        elif bonus_code == "bonus_4":
            q_index = duel["turn"]
            if q_index < len(duel["questions"]):
                duel[f"{player_key}_score"] += 1
                await query.edit_message_text("⭐ «Автопобеда»! Вопрос засчитан.")
                duel["turn"] += 1
                if duel["current_player"] == duel["player1"]:
                    duel["current_player"] = duel["player2"]
                else:
                    duel["current_player"] = duel["player1"]
                await asyncio.sleep(0.5)
                await ask_question(update, context, duel_id)
        else:
            await query.edit_message_text(f"🔍 Бонус активирован!")

    elif action == "sur":
        # sur|duel_id|player_id
        _, duel_id, player_id = parts
        player_id = int(player_id)
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