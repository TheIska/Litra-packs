from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user, update_user, add_coins
from ..models.questions import QUESTIONS
import random
import datetime
import asyncio

active_quizzes = {}
quiz_answers = {}
QUIZ_QUESTIONS_COUNT = 5


def declension_days(count):
    """Правильное склонение слова 'день'"""
    if 11 <= count % 100 <= 14:
        return "дней"
    elif count % 10 == 1:
        return "день"
    elif 2 <= count % 10 <= 4:
        return "дня"
    else:
        return "дней"


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except:
            pass
        user_id = query.from_user.id
        chat_id = query.message.chat_id
        message_id = query.message.message_id
    else:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        message_id = None

    if user_id in active_quizzes:
        text = "⏳ У тебя уже есть активная викторина! Отвечай на вопросы."
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Завершить", callback_data="stop_quiz")]])
        if query:
            try:
                await query.edit_message_text(text, reply_markup=keyboard)
            except:
                await context.bot.send_message(chat_id, text, reply_markup=keyboard)
        else:
            await update.message.reply_text(text, reply_markup=keyboard)
        return

    user = get_user(user_id)
    today = datetime.datetime.now().date().isoformat()
    last_date = user.get("daily_quiz_last_date")
    
    # Проверяем серию — увеличиваем ТОЛЬКО если играл вчера
    streak = user.get("daily_quiz_streak", 0)
    
    if last_date:
        last_date_obj = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
        today_obj = datetime.datetime.now().date()
        days_diff = (today_obj - last_date_obj).days
        
        # Если пропустил день — сбрасываем серию
        if days_diff > 1:
            update_user(user_id, daily_quiz_streak=0)
            user = get_user(user_id)
            streak = 0
        elif days_diff == 1:
            # Играл вчера — серия увеличивается на 1
            new_streak = streak + 1
            update_user(user_id, daily_quiz_streak=new_streak)
            user = get_user(user_id)
            streak = new_streak
    
    # Если новый день — сбрасываем счётчик бонусов
    if last_date and last_date != today:
        update_user(user_id, daily_quiz_done=0)
        user = get_user(user_id)
    
    bonus_count = user.get("daily_quiz_done", 0)
    streak = user.get("daily_quiz_streak", 0)
    
    # Рассчитываем награду за день (50 + 10 * streak, но не больше 100)
    daily_reward = min(50 + streak * 10, 100)

    # Проверяем, получал ли уже бонус сегодня
    if bonus_count >= 5:
        days_word = declension_days(streak)
        text = (
            f"✅ Ты уже получил все 5 бонусов за сегодня!\n"
            f"💰 Твой баланс: {user['coins']} монет\n"
            f"🔥 Серия: {streak} {days_word}\n"
            f"💎 Награда за следующий день: {min(daily_reward + 10, 100)} монет\n\n"
            "Завтра в 00:00 бонусы обновятся! 🎉"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Играть без бонусов", callback_data="quiz")],
            [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]
        ])
        if query:
            try:
                await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
            except:
                await context.bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return

    questions = random.sample(QUESTIONS, min(QUIZ_QUESTIONS_COUNT, len(QUESTIONS)))
    
    quiz_data = {
        "questions": questions,
        "current": 0,
        "score": 0,
        "total": len(questions),
        "bonus_count": bonus_count,
        "user_id": user_id,
        "chat_id": chat_id,
        "message_id": message_id,
        "daily_reward": daily_reward,
        "streak": streak
    }
    active_quizzes[user_id] = quiz_data
    quiz_answers[user_id] = 0

    await send_question(update, context, user_id, chat_id)


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int) -> None:
    quiz = active_quizzes.get(user_id)
    if not quiz:
        return

    current = quiz["current"]
    total = quiz["total"]
    
    if current >= total:
        await finish_quiz(update, context, user_id)
        return

    question_data = quiz["questions"][current]
    text = question_data["text"]
    options = question_data["options"]
    correct = question_data["correct"]

    quiz["correct"] = correct

    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"qans_{user_id}_{i}")])

    keyboard.append([InlineKeyboardButton("❌ Завершить", callback_data="stop_quiz")])

    user = get_user(user_id)
    bonus_left = 5 - user.get("daily_quiz_done", 0)
    streak = user.get("daily_quiz_streak", 0)
    daily_reward = min(50 + streak * 10, 100)
    days_word = declension_days(streak)
    
    text_message = (
        f"📝 *Вопрос {current + 1}/{total}*\n\n"
        f"{text}\n\n"
        f"💰 Награда за правильный ответ: *{daily_reward} монет*\n"
        f"🔥 Серия: *{streak} {days_word}*\n"
    )
    
    if bonus_left > 0:
        text_message += f"📊 Осталось бонусов за сегодня: *{bonus_left}*"
    else:
        text_message += f"📊 Все бонусы получены, но играй дальше! 🎉"

    try:
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(
                    text_message,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
                return
            except Exception as e:
                if "Message is not modified" in str(e):
                    return
        await context.bot.send_message(
            chat_id,
            text_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"❌ Ошибка отправки вопроса: {e}")


async def quiz_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    
    if not data.startswith("qans_"):
        return
    
    try:
        await query.answer()
    except:
        pass
    
    try:
        _, user_id_str, answer_idx = data.split("_")
        user_id = int(user_id_str)
        answer_idx = int(answer_idx)
    except ValueError:
        try:
            await query.edit_message_text("❌ Ошибка! Попробуйте снова.")
        except:
            pass
        return

    quiz = active_quizzes.get(user_id)
    if not quiz:
        try:
            await query.edit_message_text(
                "❌ Викторина завершена или неактивна.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]])
            )
        except:
            pass
        return

    correct = quiz.get("correct")
    is_correct = (answer_idx == correct)
    
    user = get_user(user_id)
    today = datetime.datetime.now().date().isoformat()
    
    # Проверяем дату для серии
    last_date = user.get("daily_quiz_last_date")
    if last_date:
        last_date_obj = datetime.datetime.strptime(last_date, "%Y-%m-%d").date()
        today_obj = datetime.datetime.now().date()
        days_diff = (today_obj - last_date_obj).days
        
        if days_diff > 1:
            update_user(user_id, daily_quiz_streak=0)
            user = get_user(user_id)
        # Серия увеличивается в quiz_command, а не здесь
    
    if user.get("daily_quiz_last_date") != today:
        update_user(user_id, daily_quiz_done=0)
        user = get_user(user_id)
    
    bonus_count = user.get("daily_quiz_done", 0)
    streak = user.get("daily_quiz_streak", 0)
    daily_reward = min(50 + streak * 10, 100)
    
    if is_correct:
        if bonus_count < 5:
            add_coins(user_id, daily_reward)
            new_done = bonus_count + 1
            update_user(user_id, 
                        daily_quiz_done=new_done,
                        daily_quiz_last_date=today)
            
            next_reward = min(50 + streak * 10, 100)
            days_word = declension_days(streak)
            
            await query.edit_message_text(
                f"✅ *Правильно!* +{daily_reward} монет! 💰\n\n"
                f"📊 Получено бонусов сегодня: {new_done}/5\n"
                f"🔥 Серия: {streak} {days_word}\n"
                f"💰 Твой баланс: {user['coins'] + daily_reward} монет",
                parse_mode="Markdown"
            )
        else:
            await query.edit_message_text(
                f"✅ *Правильно!* 🎉\n\n"
                f"📊 Ты уже получил все 5 бонусов за сегодня!\n"
                f"🔥 Серия: {streak} {declension_days(streak)}\n"
                f"💰 Твой баланс: {user['coins']} монет\n\n"
                "Продолжай играть! 🚀",
                parse_mode="Markdown"
            )
        await asyncio.sleep(1)
    else:
        await query.edit_message_text(
            f"❌ *Неправильно.*\n\n"
            f"Правильный ответ: {quiz['questions'][quiz['current']]['options'][correct]}",
            parse_mode="Markdown"
        )
        await asyncio.sleep(1.5)

    quiz["current"] += 1
    
    if quiz["current"] >= quiz["total"]:
        await finish_quiz(update, context, user_id)
    else:
        await send_question(update, context, user_id, query.message.chat_id)


async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    quiz = active_quizzes.pop(user_id, None)
    quiz_answers.pop(user_id, None)
    
    if not quiz:
        return
    
    user = get_user(user_id)
    streak = user.get("daily_quiz_streak", 0)
    next_reward = min(50 + streak * 10, 100)
    days_word = declension_days(streak)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Начать новую викторину", callback_data="quiz")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]
    ])
    
    done = user.get("daily_quiz_done", 0)
    
    if done >= 5:
        text = (
            f"🎉 *Викторина завершена!*\n\n"
            f"💰 Ты получил все *5 бонусов* за сегодня!\n"
            f"📊 Всего монет: *{user['coins']}*\n"
            f"🔥 Серия: *{streak} {days_word}*\n"
            f"💎 Завтрашняя награда: *{next_reward} монет*\n\n"
            "🔄 Можешь продолжать играть, но бонусы будут завтра!"
        )
    else:
        text = (
            f"🎉 *Викторина завершена!*\n\n"
            f"💰 Ты получил *{done}* бонусов из 5 сегодня\n"
            f"📊 Всего монет: *{user['coins']}*\n"
            f"🔥 Серия: *{streak} {days_word}*\n"
            f"💎 Завтрашняя награда: *{next_reward} монет*\n\n"
            f"💡 Осталось бонусов: *{5 - done}*\n"
            "Начни новую викторину, чтобы получить их!"
        )
    
    try:
        if update.callback_query and update.callback_query.message:
            await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await context.bot.send_message(
                chat_id=quiz.get("chat_id", user_id),
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
    except:
        pass


async def stop_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    
    if query:
        try:
            await query.answer()
        except:
            pass
        user_id = query.from_user.id
        chat_id = query.message.chat_id
    else:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

    if user_id in active_quizzes:
        del active_quizzes[user_id]
        quiz_answers.pop(user_id, None)
        
        text = "⏹️ *Викторина завершена!*"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Начать новую", callback_data="quiz")],
            [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]
        ])
        
        try:
            if query:
                await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
            else:
                await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        except:
            await context.bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        text = "❌ У тебя нет активной викторины."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📝 Начать викторину", callback_data="quiz")],
            [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]
        ])
        try:
            if query:
                await query.edit_message_text(text, reply_markup=keyboard)
            else:
                await update.message.reply_text(text, reply_markup=keyboard)
        except:
            await context.bot.send_message(chat_id, text, reply_markup=keyboard)