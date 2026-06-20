i# bot/handlers/quiz.py

import random
import asyncio
from datetime import datetime, timezone, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user, update_user, add_coins
from ..models.questions import QUESTIONS
from ..utils.helpers import shuffle_question, extract_work

active_quizzes = {}
MOSCOW_TZ = timezone(timedelta(hours=3))

def get_moscow_date():
    return datetime.now(MOSCOW_TZ).date()

def get_daily_bonus(streak: int) -> int:
    if streak >= 6:
        return 100
    return 50 + (streak - 1) * 10


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🔄 quiz_command вызван!")  # Отладочный вывод
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

    user = get_user(user_id)
    today = get_moscow_date()
    
    if user.get("daily_quiz_last_date"):
        last_date = datetime.fromisoformat(user["daily_quiz_last_date"]).date()
        if last_date == today:
            if user.get("daily_quiz_done", 0) == 1:
                streak = user.get("daily_quiz_streak", 0)
                bonus = get_daily_bonus(streak)
                await context.bot.send_message(
                    chat_id,
                    f"✅ *Ежедневная викторина уже пройдена!*\n\n"
                    f"📊 Текущая серия: *{streak} дней*\n"
                    f"💰 Завтрашний бонус: *{get_daily_bonus(streak + 1)} монет*\n\n"
                    f"Приходи завтра после 00:00 МСК!",
                    parse_mode="Markdown"
                )
                return
    
    if user.get("daily_quiz_last_date"):
        last_date = datetime.fromisoformat(user["daily_quiz_last_date"]).date()
        if last_date < today - timedelta(days=1):
            update_user(user_id, daily_quiz_streak=0)
            user["daily_quiz_streak"] = 0
    
    questions = random.sample(QUESTIONS, 5)
    quiz_id = f"quiz_{user_id}_{int(datetime.now().timestamp())}"
    
    active_quizzes[quiz_id] = {
        "user_id": user_id,
        "questions": questions,
        "current_question": 0,
        "correct_answers": 0,
        "streak": user.get("daily_quiz_streak", 0),
        "bonus": get_daily_bonus(user.get("daily_quiz_streak", 0) + 1),
    }
    
    await show_quiz_question(update, context, quiz_id)


async def show_quiz_question(update, context, quiz_id):
    quiz = active_quizzes.get(quiz_id)
    if not quiz:
        return
    
    user_id = quiz["user_id"]
    q_index = quiz["current_question"]
    questions = quiz["questions"]
    
    if q_index >= len(questions):
        await finish_quiz(update, context, quiz_id)
        return
    
    question = shuffle_question(questions[q_index])
    
    work = question.get("work", "")
    if not work:
        work = extract_work(question.get("text", ""))
    
    work_text = f"\n📖 *{work}*" if work else ""
    
    text = (
        f"📝 *Ежедневная викторина*\n"
        f"Вопрос {q_index + 1} из 5\n"
        f"Серия: {quiz['streak']} дней\n"
        f"💰 Бонус за 5 ответов: {quiz['bonus']} монет\n\n"
        f"{question['text']}"
        f"{work_text}\n\n"
        f"_Выбери вариант ответа:_"
    )
    
    keyboard = []
    for idx, option in enumerate(question["options"]):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"qans|{quiz_id}|{idx}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await context.bot.send_message(
            user_id,
            text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


async def quiz_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    parts = data.split("|")
    quiz_id = parts[1]
    answer_idx = int(parts[2])
    
    quiz = active_quizzes.get(quiz_id)
    if not quiz:
        await query.edit_message_text("❌ Викторина уже завершена.")
        return
    
    user_id = quiz["user_id"]
    q_index = quiz["current_question"]
    questions = quiz["questions"]
    
    if q_index >= len(questions):
        await query.edit_message_text("❌ Викторина уже завершена.")
        return
    
    question = questions[q_index]
    correct = question["correct"]
    is_correct = (answer_idx == correct)
    
    correct_text = question["options"][correct]
    
    if is_correct:
        quiz["correct_answers"] += 1
        await query.edit_message_text(
            f"✅ *Правильно!*\n\n"
            f"Правильный ответ: {correct_text}\n"
            f"Прогресс: {quiz['correct_answers']}/5",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            f"❌ *Неправильно.*\n\n"
            f"Правильный ответ: {correct_text}\n"
            f"Прогресс: {quiz['correct_answers']}/5",
            parse_mode="Markdown"
        )
    
    quiz["current_question"] += 1
    
    await asyncio.sleep(1.5)
    await show_quiz_question(update, context, quiz_id)


async def finish_quiz(update, context, quiz_id):
    quiz = active_quizzes.pop(quiz_id, None)
    if not quiz:
        return
    
    user_id = quiz["user_id"]
    correct = quiz["correct_answers"]
    streak = quiz["streak"]
    bonus = quiz["bonus"]
    
    today = get_moscow_date()
    
    if correct >= 5:
        new_streak = streak + 1
        add_coins(user_id, bonus)
        update_user(
            user_id,
            daily_quiz_streak=new_streak,
            daily_quiz_last_date=today.isoformat(),
            daily_quiz_done=1
        )
        
        await context.bot.send_message(
            user_id,
            f"🎉 *Викторина завершена!*\n\n"
            f"✅ Все 5 ответов правильные!\n"
            f"💰 Ты получил *{bonus} монет*\n"
            f"📊 Текущая серия: *{new_streak} дней*\n\n"
            f"Завтра бонус будет *{get_daily_bonus(new_streak + 1)} монет*",
            parse_mode="Markdown"
        )
    else:
        update_user(
            user_id,
            daily_quiz_last_date=today.isoformat(),
            daily_quiz_done=1
        )
        
        await context.bot.send_message(
            user_id,
            f"📝 *Викторина завершена!*\n\n"
            f"✅ Правильных ответов: {correct}/5\n"
            f"❌ Неправильных: {5 - correct}\n\n"
            f"Чтобы получить бонус, нужно ответить правильно на все 5 вопросов!\n"
            f"📊 Серия не прервалась — завтра продолжится.",
            parse_mode="Markdown"
        )