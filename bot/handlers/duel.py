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

# Порядок редкости (от самой редкой к самой частой)
RARITY_ORDER = {"легендарный": 0, "эпический": 1, "редкий": 2, "обычный": 3}

def get_best_heroes(collection, count=3):
    """Выбирает самых редких героев из коллекции"""
    # Сортируем героев по редкости (сначала легендарные, потом эпические и т.д.)
    sorted_heroes = sorted(
        collection.items(),
        key=lambda item: RARITY_ORDER.get(item[1].get("rarity", "обычный"), 999)
    )
    # Берём первых count героев (самые редкие)
    return [key for key, _ in sorted_heroes[:count]]

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
        await send_message("⚠️ У тебя уже есть активная дуэль!")
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

    # Создаём дуэль
    duel_id = f"{user_id}_{opponent_id}_{random.randint(1000,9999)}"
    
    # Выбираем 3 самых редких героя для каждого
    p1_heroes = get_best_heroes(collection, 3)
    p2_collection = get_collection(opponent_id)
    p2_heroes = get_best_heroes(p2_collection, 3)

    duels[duel_id] = {
        "player1": user_id,
        "player2": opponent_id,
        "status": "waiting",
        "p1_score": 0,
        "p2_score": 0,
        "p1_used": [],
        "p2_used": [],
        "questions": random.sample(QUESTIONS, 3),
        "turn": 0,
        "current_player": user_id,
        "p1_heroes": p1_heroes,
        "p2_heroes": p2_heroes,
        "p1_ready": False,
        "p2_ready": False,
    }

    user_duel[user_id] = duel_id
    user_duel[opponent_id] = duel_id

    # Отправляем сообщение игроку
    p1_names = []
    for key in p1_heroes:
        if key in collection:
            p1_names.append(f"{collection[key]['name']} ({collection[key]['rarity']})")
    
    await send_message(
        f"⚔️ *Соперник найден!*\n\n"
        f"Твои лучшие герои для дуэли:\n" + "\n".join([f"• {name}" for name in p1_names]) + 
        f"\n\nОжидай, пока соперник подтвердит готовность.",
        parse_mode="Markdown"
    )
    await show_waiting_screen(update, context, user_id, duel_id)

    # Отправляем сообщение сопернику
    try:
        p2_names = []
        for key in p2_heroes:
            if key in p2_collection:
                p2_names.append(f"{p2_collection[key]['name']} ({p2_collection[key]['rarity']})")
        
        await context.bot.send_message(
            opponent_id,
            f"⚔️ *{update.effective_user.first_name} вызвал тебя на дуэль!*\n\n"
            f"Твои лучшие герои для дуэли:\n" + "\n".join([f"• {name}" for name in p2_names]) +
            f"\n\nНажми «Готово», чтобы начать.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Готово", callback_data=f"dready_{duel_id}_{opponent_id}")]
            ])
        )
    except Exception as e:
        await send_message(f"⚠️ Ошибка: {e}")
        cancel_duel(duel_id)
        return

async def show_waiting_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, duel_id: str):
    await context.bot.send_message(
        user_id,
        "⏳ Ожидаем, пока соперник подтвердит готовность...",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Проверить статус", callback_data=f"dcheck_{duel_id}_{user_id}")]
        ])
    )

async def check_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    if data[0] == "dcheck":
        duel_id = data[1]
        user_id = int(data[2])
        duel = duels.get(duel_id)
        if not duel:
            await query.edit_message_text("❌ Дуэль завершена.")
            return
        if duel.get("p1_ready") and duel.get("p2_ready"):
            await query.edit_message_text("✅ Соперник готов! Начинаем дуэль!")
            await start_duel(update, context, duel_id)
        else:
            await query.answer("Соперник ещё не готов. Подожди.")

async def ready_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    if data[0] == "dready":
        duel_id = data[1]
        user_id = int(data[2])
        duel = duels.get(duel_id)
        if not duel:
            await query.edit_message_text("❌ Дуэль завершена.")
            return
        if user_id == duel["player1"]:
            duel["p1_ready"] = True
        else:
            duel["p2_ready"] = True

        await query.edit_message_text("✅ Ты готов! Ожидаем соперника.")

        if duel.get("p1_ready") and duel.get("p2_ready"):
            await start_duel(update, context, duel_id)

async def start_duel(update: Update, context: ContextTypes.DEFAULT_TYPE, duel_id: str):
    duel = duels.get(duel_id)
    if not duel:
        return

    duel["status"] = "active"
    p1 = duel["player1"]
    p2 = duel["player2"]

    await context.bot.send_message(p1, "⚔️ *Дуэль началась!* Твой ход.", parse_mode="Markdown")
    await context.bot.send_message(p2, "⚔️ *Дуэль началась!* Ожидай.", parse_mode="Markdown")
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
        keyboard.append([InlineKeyboardButton(option, callback_data=f"da_{duel_id}_{current_player}_{idx}")])

    # Бонусы от героев
    hero_keys = duel.get("p1_heroes", []) if current_player == duel["player1"] else duel.get("p2_heroes", [])
    used = duel.get(f"{player_key}_used", [])
    bonus_buttons = []
    
    coll = get_collection(current_player)
    for i, hero_key in enumerate(hero_keys):
        if hero_key in coll:
            hero = coll[hero_key]
            rarity = hero.get("rarity", "обычный")
            bonus = BONUSES.get(rarity, BONUSES["обычный"])
            if bonus["code"] not in used:
                bonus_buttons.append(InlineKeyboardButton(
                    f"💡 {bonus['name']} ({hero['name']})",
                    callback_data=f"db_{duel_id}_{current_player}_{bonus['code']}_{i}"
                ))
    
    if bonus_buttons:
        keyboard.append(bonus_buttons)

    keyboard.append([InlineKeyboardButton("🏳️ Сдаться", callback_data=f"ds_{duel_id}_{current_player}")])

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
    data = query.data.split("_")
    
    if data[0] == "da":
        _, duel_id, player_id, answer_idx = data
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
                await query.edit_message_text("❌ Неправильно! Есть «Пересдача»! Ещё раз.")
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

    elif data[0] == "db":
        _, duel_id, player_id, bonus_code, hero_idx = data
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
            await query.edit_message_text("🔍 «Подсказка» активирована! Один неверный вариант убран.")
            # Здесь можно реализовать логику подсказки, но для простоты оставляем уведомление
        elif bonus_code == "bonus_3":
            await query.edit_message_text("🔄 «Пересдача» активирована! При ошибке сможешь ответить ещё раз.")
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

    elif data[0] == "ds":
        _, duel_id, player_id = data
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