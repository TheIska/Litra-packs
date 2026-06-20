# bot/handlers/quiz.py

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


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает викторину — 50 монет за первые 5 правильных ответов"""
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

    # Проверяем, есть ли уже активная викторина
    for qid, quiz in active_quizzes.items():
        if quiz["user_id"] == user_id and not quiz.get("is_finished", False):
            await show_quiz_question(update, context, qid)
            return
    
    # Создаём новую викторину
    all_questions = random.sample(QUESTIONS, len(QUESTIONS))
    
    quiz_id = f"quiz_{user_id}_{int(datetime.now().timestamp())}"
    
    active_quizzes[quiz_id] = {
        "user_id": user_id,
        "all_questions": all_questions,
        "current_index": 0,
        "correct_count": 0,           # Счётчик правильных ответов (всего)
        "rewarded_count": 0,          # Сколько раз уже дали монеты (макс 5)
        "wrong_total": 0,             # Всего неправильных ответов
        "coins_earned": 0,            # Всего заработано монет
        "is_finished": False,
    }
    
    await show_quiz_question(update, context, quiz_id)


async def show_quiz_question(update, context, quiz_id):
    quiz = active_quizzes.get(quiz_id)
    if not quiz or quiz.get("is_finished", False):
        return
    
    user_id = quiz["user_id"]
    all_questions = quiz["all_questions"]
    current_index = quiz["current_index"]
    
    if current_index >= len(all_questions):
        random.shuffle(all_questions)
        quiz["current_index"] = 0
        current_index = 0
    
    question = shuffle_question(all_questions[current_index])
    
    work = question.get("work", "")
    if not work:
        work = extract_work(question.get("text", ""))
    
    work_text = f"\n📖 *{work}*" if work else ""
    
    rewarded = quiz['rewarded_count']
    remaining = 5 - rewarded
    
    text = (
        f"📝 *Викторина*\n"
        f"💰 50 монет за каждый из первых 5 правильных ответов\n"
        f"✅ Правильных: {quiz['correct_count']} (осталось бонусов: {remaining})\n"
        f"❌ Неправильных: {quiz['wrong_total']}\n"
        f"💵 Заработано: {quiz['coins_earned']} монет\n\n"
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
    if not quiz or quiz.get("is_finished", False):
        await query.edit_message_text("❌ Викторина уже завершена.")
        return
    
    user_id = quiz["user_id"]
    all_questions = quiz["all_questions"]
    current_index = quiz["current_index"]
    
    if current_index >= len(all_questions):
        random.shuffle(all_questions)
        quiz["current_index"] = 0
        current_index = 0
    
    question = all_questions[current_index]
    correct = question["correct"]
    is_correct = (answer_idx == correct)
    
    correct_text = question["options"][correct]
    
    if is_correct:
        quiz["correct_count"] += 1
        
        # Проверяем, можно ли дать монеты (только первые 5 правильных)
        if quiz["rewarded_count"] < 5:
            add_coins(user_id, 50)
            quiz["coins_earned"] += 50
            quiz["rewarded_count"] += 1
            rewarded = quiz["rewarded_count"]
            
            await query.edit_message_text(
                f"✅ *Правильно!*\n\n"
                f"Правильный ответ: {correct_text}\n"
                f"💰 +50 монет! ({rewarded}/5)\n"
                f"💵 Всего заработано: {quiz['coins_earned']} монет",
                parse_mode="Markdown"
            )
        else:
            # Лимит исчерпан — просто показываем, что правильно, но без монет
            await query.edit_message_text(
                f"✅ *Правильно!*\n\n"
                f"Правильный ответ: {correct_text}\n"
                f"💵 Всего заработано: {quiz['coins_earned']} монет\n\n"
                f"_Ты уже получил все 5 бонусов! Отвечай дальше для удовольствия._",
                parse_mode="Markdown"
            )
    else:
        quiz["wrong_total"] += 1
        
        await query.edit_message_text(
            f"❌ *Неправильно.*\n\n"
            f"Правильный ответ: {correct_text}\n"
            f"💵 Всего заработано: {quiz['coins_earned']} монет\n\n"
            f"_Не расстраивайся! Отвечай дальше._",
            parse_mode="Markdown"
        )
    
    quiz["current_index"] += 1
    
    await asyncio.sleep(1.5)
    await show_quiz_question(update, context, quiz_id)


async def stop_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Останавливает викторину"""
    user_id = update.effective_user.id
    
    for quiz_id, quiz in list(active_quizzes.items()):
        if quiz["user_id"] == user_id and not quiz.get("is_finished", False):
            quiz["is_finished"] = True
            earned = quiz["coins_earned"]
            rewarded = quiz["rewarded_count"]
            await update.message.reply_text(
                f"🏁 *Викторина завершена!*\n\n"
                f"💰 Ты заработал *{earned} монет* ({rewarded}/5 бонусов)\n"
                f"✅ Правильных ответов: {quiz['correct_count']}\n"
                f"❌ Неправильных: {quiz['wrong_total']}\n\n"
                f"_Отправь /quiz, чтобы начать заново_",
                parse_mode="Markdown"
            )
            active_quizzes.pop(quiz_id, None)
            return
    
    await update.message.reply_text("❌ У тебя нет активной викторины.")