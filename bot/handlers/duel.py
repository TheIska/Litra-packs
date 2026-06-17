import random
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_collection, get_user, update_duel_stats, get_opponent
from ..models.questions import QUESTIONS

# Хранилище активных дуэлей (в памяти)
duels = {}
user_duel = {}

# Бонусы карточек по редкости
BONUSES = {
    "обычный": {"name": "Уверенность", "effect": "+1 очко", "code": "bonus_1"},
    "редкий": {"name": "Подсказка", "effect": "убрать вариант", "code": "bonus_2"},
    "эпический": {"name": "Пересдача", "effect": "ответить ещё раз", "code": "bonus_3"},
    "легендарный": {"name": "Автопобеда", "effect": "автоправильный ответ", "code": "bonus_4"},
}

async def duel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /duel — начать поиск соперника"""
    query = update.callback_query
    if query:
        await query.answer()
        user_id = query.from_user.id
        send_message = query.edit_message_text
    else:
        user_id = update.effective_user.id
        send_message = update.message.reply_text

    # Проверка: есть ли уже активная дуэль
    if user_id in user_duel:
        await send_message("⚠️ У тебя уже есть активная дуэль! Заверши её.")
        return

    # Проверка: есть ли минимум 3 героя
    collection = get_collection(user_id)
    if len(collection) < 3:
        await send_message("❌ У тебя меньше 3 героев в коллекции. Открой паки, чтобы участвовать в дуэлях!")
        return

    # Поиск соперника
    opponent_id = get_opponent(user_id)
    if not opponent_id:
        await send_message("😴 Сейчас нет других игроков. Попробуй позже.")
        return

    if opponent_id in user_duel:
        await send_message("Соперник уже в игре. Попробуй ещё раз.")
        return

    # Создаём дуэль
    duel_id = f"{user_id}_{opponent_id}_{random.randint(1000,9999)}"
    duels[duel_id] = {
        "player1": user_id,
        "player2": opponent_id,
        "status": "waiting",
        "p1_score": 0,
        "p2_score": 0,
        "p1_bonuses": [],
        "p2_bonuses": [],
        "p1_used": [],
        "p2_used": [],
        "questions": random.sample(QUESTIONS, 5),
        "turn": 0,
        "current_player": user_id,
        "p1_chosen_cards": [],
        "p2_chosen_cards": [],
    }

    user_duel[user_id] = duel_id
    user_duel[opponent_id] = duel_id

    # Уведомляем инициатора
    await send_message("⚔️ *Поиск соперника успешен!* Сейчас выбери 3 героя для бонусов.", parse_mode="Markdown")
    await show_card_selection(update, context, user_id, duel_id)

    # Уведомляем соперника
    try:
        await context.bot.send_message(
            opponent_id,
            f"⚔️ *{update.effective_user.first_name} вызвал тебя на дуэль!*\nВыбери 3 героя для бонусов.",
            parse_mode="Markdown"
        )
        await show_card_selection(update, context, opponent_id, duel_id, is_opponent=True)
    except Exception as e:
        await send_message(f"⚠️ Не удалось связаться с соперником. Отменяем дуэль. Ошибка: {e}")
        cancel_duel(duel_id)
        return

async def show_card_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, duel_id: str, is_opponent=False):
    """Показывает выбор карточек для бонусов"""
    collection = get_collection(user_id)
    if not collection:
        await context.bot.send_message(user_id, "❌ У тебя нет героев для дуэли.")
        return

    items = list(collection.items())[:15]  # показываем первые 15 героев
    keyboard = []
    for key, hero in items:
        keyboard.append([InlineKeyboardButton(
            f"{hero['name']} ({hero['rarity']})",
            callback_data=f"duel_card_{duel_id}_{user_id}_{key}"
        )])
    keyboard.append([InlineKeyboardButton("✅ Готово (выбрано 3)", callback_data=f"duel_ready_{duel_id}_{user_id}")])

    await context.bot.send_message(
        user_id,
        "🃏 Выбери 3 героя для бонусов (нажми на них, затем «Готово»):",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def card_selection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    
    if data[1] == "card":
        # Формат: duel_card_{duel_id}_{user_id}_{hero_key}
        _, _, duel_id, user_id, hero_key = data
        user_id = int(user_id)
        duel = duels.get(duel_id)
        if not duel:
            await query.edit_message_text("❌ Дуэль уже завершена.")
            return

        # Определяем, для кого выбираем
        if user_id == duel["player1"]:
            selected = duel.setdefault("p1_chosen_cards", [])
        else:
            selected = duel.setdefault("p2_chosen_cards", [])

        if hero_key in selected:
            await query.answer("Этот герой уже выбран.")
            return
        if len(selected) >= 3:
            await query.answer("Ты уже выбрал 3 героя.")
            return

        selected.append(hero_key)
        await query.answer("Герой добавлен!")
        remaining = 3 - len(selected)
        await query.edit_message_text(
            f"🃏 Выбрано {len(selected)} из 3. Осталось {remaining}.\n\n"
            "Когда выберешь всех, нажми «Готово».",
            reply_markup=query.message.reply_markup
        )

    elif data[1] == "ready":
        # Формат: duel_ready_{duel_id}_{user_id}
        _, _, duel_id, user_id = data
        user_id = int(user_id)
        duel = duels.get(duel_id)
        if not duel:
            await query.edit_message_text("❌ Дуэль уже завершена.")
            return

        if user_id == duel["player1"]:
            selected = duel.get("p1_chosen_cards", [])
        else:
            selected = duel.get("p2_chosen_cards", [])

        if len(selected) < 3:
            await query.answer("Выбери ровно 3 героя!")
            return

        await query.edit_message_text("✅ Герои выбраны! Ожидаем соперника.")

        # Проверяем, выбрали ли оба
        if len(duel.get("p1_chosen_cards", [])) >= 3 and len(duel.get("p2_chosen_cards", [])) >= 3:
            await start_duel(update, context, duel_id)

async def start_duel(update: Update, context: ContextTypes.DEFAULT_TYPE, duel_id: str):
    duel = duels.get(duel_id)
    if not duel:
        return

    duel["status"] = "active"
    p1 = duel["player1"]
    p2 = duel["player2"]

    # Превращаем выбранные карточки в бонусы с описаниями
    for pid in [p1, p2]:
        bonuses = []
        key = "p1_chosen_cards" if pid == p1 else "p2_chosen_cards"
        for hero_key in duel.get(key, []):
            coll = get_collection(pid)
            if hero_key in coll:
                hero = coll[hero_key]
                rarity = hero.get("rarity", "обычный")
                bonuses.append({
                    "hero": hero["name"],
                    "rarity": rarity,
                    "bonus": BONUSES.get(rarity, BONUSES["обычный"])
                })
        duel[f"p{1 if pid == p1 else 2}_bonuses"] = bonuses

    await context.bot.send_message(p1, "⚔️ *Дуэль начинается!* Первый вопрос для тебя.", parse_mode="Markdown")
    await context.bot.send_message(p2, "⚔️ *Дуэль начинается!* Ожидай своего хода.", parse_mode="Markdown")
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

    # Кнопки с вариантами ответов
    keyboard = []
    for idx, option in enumerate(question["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"duel_answer_{duel_id}_{current_player}_{idx}")])

    # Кнопки бонусов (если есть неиспользованные)
    bonuses = duel.get(f"{player_key}_bonuses", [])
    used = duel.get(f"{player_key}_used", [])
    bonus_buttons = []
    for b in bonuses:
        if b["bonus"]["code"] not in used:
            bonus_buttons.append(InlineKeyboardButton(
                f"💡 {b['bonus']['name']} ({b['hero']})",
                callback_data=f"duel_bonus_{duel_id}_{current_player}_{b['bonus']['code']}"
            ))
    if bonus_buttons:
        keyboard.append(bonus_buttons)

    await context.bot.send_message(
        current_player,
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Уведомляем соперника
    opponent = duel["player2"] if current_player == duel["player1"] else duel["player1"]
    await context.bot.send_message(
        opponent,
        f"⏳ Сейчас ход твоего соперника. Вопрос {q_index+1}."
    )

async def answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    
    if data[1] == "answer":
        # Формат: duel_answer_{duel_id}_{player_id}_{answer_idx}
        _, _, duel_id, player_id, answer_idx = data
        player_id = int(player_id)
        answer_idx = int(answer_idx)
        duel = duels.get(duel_id)
        if not duel or duel["status"] != "active" or duel["current_player"] != player_id:
            await query.edit_message_text("⏳ Сейчас не твой ход или дуэль завершена.")
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
            # Проверяем, есть ли бонус "Пересдача"
            used = duel.get(f"{player_key}_used", [])
            if "bonus_3" in used:
                await query.edit_message_text("❌ Неправильно, но у тебя есть «Пересдача»! Попробуй ещё раз.")
                # Не увеличиваем turn, чтобы задать тот же вопрос
                await ask_question(update, context, duel_id)
                return
            else:
                await query.edit_message_text("❌ *Неправильно.*", parse_mode="Markdown")

        # Переход хода
        duel["turn"] += 1
        if duel["current_player"] == duel["player1"]:
            duel["current_player"] = duel["player2"]
        else:
            duel["current_player"] = duel["player1"]

        await asyncio.sleep(0.5)
        await ask_question(update, context, duel_id)

    elif data[1] == "bonus":
        # Формат: duel_bonus_{duel_id}_{player_id}_{bonus_code}
        _, _, duel_id, player_id, bonus_code = data
        player_id = int(player_id)
        duel = duels.get(duel_id)
        if not duel:
            await query.edit_message_text("❌ Дуэль уже завершена.")
            return

        player_key = "p1" if player_id == duel["player1"] else "p2"
        used = duel.setdefault(f"{player_key}_used", [])
        if bonus_code in used:
            await query.edit_message_text("⚠️ Ты уже использовал этот бонус.")
            return

        used.append(bonus_code)

        # Применяем эффекты бонусов
        if bonus_code == "bonus_1":  # Уверенность
            duel[f"{player_key}_score"] += 1
            await query.edit_message_text("💪 Бонус «Уверенность»! +1 очко за этот вопрос.")
        elif bonus_code == "bonus_4":  # Автопобеда
            q_index = duel["turn"]
            if q_index < len(duel["questions"]):
                duel[f"{player_key}_score"] += 1
                await query.edit_message_text("⭐ Бонус «Автопобеда»! Вопрос засчитан.")
                duel["turn"] += 1
                if duel["current_player"] == duel["player1"]:
                    duel["current_player"] = duel["player2"]
                else:
                    duel["current_player"] = duel["player1"]
                await asyncio.sleep(0.5)
                await ask_question(update, context, duel_id)
        else:
            # Для бонусов "Подсказка" и "Пересдача" просто уведомляем
            bonus_name = BONUSES.get(bonus_code, {}).get('name', 'Неизвестный')
            await query.edit_message_text(f"🔍 Бонус «{bonus_name}» активирован! Используй его при ответе.")

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

    # Удаляем дуэль из памяти
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