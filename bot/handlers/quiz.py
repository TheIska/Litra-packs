from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user, update_user, add_coins
from ..models.questions import QUESTIONS
import random
import datetime
import asyncio  # ДОБАВЛЕН ИМПОРТ

# Хранилище активных викторин
active_quizzes = {}

# Правильные ответы за викторину (для начисления монет)
quiz_answers = {}
QUIZ_QUESTIONS_COUNT = 5  # Количество вопросов за викторину

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Запускает викторину"""
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

    # Проверяем, есть ли уже активная викторина
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

    # Проверяем ежедневный бонус
    user = get_user(user_id)
    today = datetime.datetime.now().date().isoformat()
    last_date = user.get("daily_quiz_last_date")
    
    # Сбрасываем daily_quiz_done, если прошёл день
    if last_date and last_date != today:
        update_user(user_id, daily_quiz_done=0, daily_quiz_streak=0)
        user = get_user(user_id)
    
    # Проверяем, получал ли уже бонус сегодня
    if user.get("daily_quiz_done", 0) >= 5:
        text = (
            "✅ Ты уже получил все бонусы за сегодня (5 раз по 50 монет)!\n"
            f"💰 Твой баланс: {user['coins']} монет\n\n"
            "Завтра в 00:00 бонусы обновятся! 🎉"
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]])
        if query:
            try:
                await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
            except:
                await context.bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        return

    # Проверяем, сколько бонусов уже получено сегодня
    bonus_count = user.get("daily_quiz_done", 0)

    # Перемешиваем вопросы
    questions = random.sample(QUESTIONS, min(QUIZ_QUESTIONS_COUNT, len(QUESTIONS)))
    
    # Сохраняем состояние викторины
    quiz_data = {
        "questions": questions,
        "current": 0,
        "score": 0,
        "total": len(questions),
        "bonus_count": bonus_count,
        "user_id": user_id,
        "chat_id": chat_id,
        "message_id": message_id
    }
    active_quizzes[user_id] = quiz_data
    quiz_answers[user_id] = 0

    # Отправляем первый вопрос
    await send_question(update, context, user_id, chat_id)


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, chat_id: int) -> None:
    """Отправляет текущий вопрос викторины"""
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

    # Сохраняем правильный ответ для проверки
    quiz["correct"] = correct

    # Создаём клавиатуру
    keyboard = []
    for i, option in enumerate(options):
        keyboard.append([InlineKeyboardButton(option, callback_data=f"qans_{user_id}_{i}")])

    keyboard.append([InlineKeyboardButton("❌ Завершить", callback_data="stop_quiz")])

    text_message = (
        f"📝 *Вопрос {current + 1}/{total}*\n\n"
        f"{text}\n\n"
        f"💰 Бонус за правильный ответ: *50 монет*\n"
        f"📊 Осталось бонусов за сегодня: *{5 - quiz['bonus_count']}*"
    )

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
        try:
            await context.bot.send_message(
                chat_id,
                text_message,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        except:
            pass


async def quiz_answer_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ответ на вопрос викторины"""
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

    # Проверяем, что викторина активна
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

    # Проверяем, что ответ правильный
    correct = quiz.get("correct")
    is_correct = (answer_idx == correct)
    
    # Получаем данные пользователя
    user = get_user(user_id)
    today = datetime.datetime.now().date().isoformat()
    
    # Проверяем дату
    if user.get("daily_quiz_last_date") != today:
        update_user(user_id, daily_quiz_done=0, daily_quiz_streak=0)
        user = get_user(user_id)
    
    # Проверяем, не исчерпан ли лимит бонусов
    if user.get("daily_quiz_done", 0) >= 5:
        try:
            await query.edit_message_text(
                "✅ Ты уже получил все бонусы за сегодня!\n"
                "Завтра в 00:00 бонусы обновятся. 🎉",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]])
            )
        except:
            pass
        del active_quizzes[user_id]
        return

    # Если ответ правильный и есть бонусы
    if is_correct:
        # Начисляем 50 монет
        add_coins(user_id, 50)
        
        # Обновляем счётчик бонусов
        new_done = user.get("daily_quiz_done", 0) + 1
        update_user(user_id, 
                    daily_quiz_done=new_done,
                    daily_quiz_last_date=today,
                    daily_quiz_streak=user.get("daily_quiz_streak", 0) + 1)
        
        # Обновляем quiz_data
        quiz["bonus_count"] = new_done
        
        # Сообщаем о начислении
        try:
            await query.edit_message_text(
                f"✅ *Правильно!* +50 монет! 💰\n\n"
                f"📊 Получено бонусов сегодня: {new_done}/5\n"
                f"💰 Твой баланс: {user['coins'] + 50} монет",
                parse_mode="Markdown"
            )
        except:
            pass
        await asyncio.sleep(1)
    else:
        try:
            await query.edit_message_text(
                f"❌ *Неправильно.*\n\n"
                f"Правильный ответ: {quiz['questions'][quiz['current']]['options'][correct]}",
                parse_mode="Markdown"
            )
        except:
            pass
        await asyncio.sleep(1.5)

    # Переходим к следующему вопросу
    quiz["current"] += 1
    
    if quiz["current"] >= quiz["total"]:
        await finish_quiz(update, context, user_id)
    else:
        await send_question(update, context, user_id, query.message.chat_id)


async def finish_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int) -> None:
    """Завершает викторину"""
    quiz = active_quizzes.pop(user_id, None)
    quiz_answers.pop(user_id, None)
    
    if not quiz:
        return
    
    user = get_user(user_id)
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]])
    
    # Проверяем, все ли бонусы получены
    done = user.get("daily_quiz_done", 0)
    
    if done >= 5:
        text = (
            f"🎉 *Викторина завершена!*\n\n"
            f"💰 Ты получил все *5 бонусов* за сегодня!\n"
            f"📊 Всего монет: *{user['coins']}*\n"
            f"🔥 Серия: *{user.get('daily_quiz_streak', 0)}* дней\n\n"
            "Завтра в 00:00 бонусы обновятся!"
        )
    else:
        text = (
            f"🎉 *Викторина завершена!*\n\n"
            f"💰 Ты получил *{done}* бонусов из 5 сегодня\n"
            f"📊 Всего монет: *{user['coins']}*\n"
            f"🔥 Серия: *{user.get('daily_quiz_streak', 0)}* дней\n\n"
            f"💡 Осталось бонусов: *{5 - done}*\n"
            "Чтобы получить их, начни новую викторину!"
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
        try:
            await context.bot.send_message(
                chat_id=quiz.get("chat_id", user_id),
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
        except:
            pass


async def stop_quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Останавливает текущую викторину"""
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
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]])
        
        try:
            if query:
                await query.edit_message_text(text, reply_markup=keyboard, parse_mode="Markdown")
            else:
                await update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")
        except:
            await context.bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        text = "❌ У тебя нет активной викторины."
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]])
        try:
            if query:
                await query.edit_message_text(text, reply_markup=keyboard)
            else:
                await update.message.reply_text(text, reply_markup=keyboard)
        except:
            await context.bot.send_message(chat_id, text, reply_markup=keyboard)