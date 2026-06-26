from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from ..database import get_user, get_collection
from ..friends import get_friends, add_friend, is_friend, get_user_by_id
from datetime import datetime, timedelta

ADMIN_ID = 6082384471

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    collection = get_collection(user_id)

    last = user.get("last_free_pack")
    if last:
        last_time = datetime.fromisoformat(last)
        if datetime.now() - last_time < timedelta(hours=3):
            remaining = timedelta(hours=3) - (datetime.now() - last_time)
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            timer_text = f"⏳ Следующий бесплатный пак через {hours}ч {minutes}мин"
        else:
            timer_text = "✅ Бесплатный пак доступен!"
    else:
        timer_text = "✅ Бесплатный пак доступен!"

    keyboard = [
        [InlineKeyboardButton("📝 Викторина", callback_data="quiz")],
        [InlineKeyboardButton("🛒 Магазин паков", callback_data="shop")],
        [InlineKeyboardButton("📚 Мой альбом", callback_data="album")],
        [InlineKeyboardButton("⚔️ Дуэль", callback_data="duel")],
        [InlineKeyboardButton("👥 Друзья", callback_data="friends_menu")],
        [InlineKeyboardButton("📩 Сообщить об ошибке", callback_data="report_error")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_text = (
        f"📖 **Литературный Герой**\n\n"
        f"💰 Баланс: {user['coins']} монет\n"
        f"📚 Героев в альбоме: {len(collection)}\n"
        f"{timer_text}\n\n"
        "Используй кнопки ниже:"
    )

    if update.callback_query:
        query = update.callback_query
        try:
            await query.answer()
        except Exception:
            pass
        if query.message.photo:
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=welcome_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
        else:
            try:
                await query.edit_message_text(
                    welcome_text,
                    parse_mode="Markdown",
                    reply_markup=reply_markup
                )
            except Exception:
                pass
    else:
        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


async def friends_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    friends = get_friends(user_id)
    
    text = "👥 **Друзья**\n\n"
    
    if friends:
        text += f"У вас *{len(friends)}* друзей:\n\n"
        for fid in friends[:10]:
            try:
                chat = await context.bot.get_chat(fid)
                name = chat.first_name or f"ID: {fid}"
            except:
                name = f"ID: {fid}"
            text += f"• {name} (ID: `{fid}`)\n"
        if len(friends) > 10:
            text += f"\n...и ещё {len(friends) - 10} друзей"
    else:
        text += "У вас пока нет друзей.\n"
    
    text += "\n💡 **Как добавить друзей:**\n"
    text += "• По ID (если знаете)\n"
    text += "• Из списка игроков"
    
    keyboard = [
        [InlineKeyboardButton("➕ По ID", callback_data="friends_add_id")],
        [InlineKeyboardButton("📋 Из списка игроков", callback_data="friends_from_list")],
        [InlineKeyboardButton("⚔️ Дуэль с другом", callback_data="duel_friends")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def friends_add_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    
    text = (
        "➕ **Добавить друга по ID**\n\n"
        "Введите ID друга в чат.\n"
        "ID можно узнать, отправив команду `/id` в личные сообщения боту.\n\n"
        "Например: `123456789`"
    )
    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="friends_menu")]]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    context.user_data['waiting_for_friend_id'] = True


async def friends_from_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    chat_id = query.message.chat_id
    
    from ..database import get_all_users
    users = get_all_users()
    friends = get_friends(user_id)
    
    available_users = [u for u in users if u["user_id"] != user_id and u["user_id"] not in friends]
    
    if not available_users:
        await query.edit_message_text(
            "😴 Нет доступных игроков для добавления.\n\nВсе игроки уже у вас в друзьях!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="friends_menu")]])
        )
        return
    
    keyboard = []
    for user in available_users[:20]:
        try:
            chat = await context.bot.get_chat(user["user_id"])
            name = chat.first_name or f"ID: {user['user_id']}"
        except:
            name = f"ID: {user['user_id']}"
        hero_count = len(get_collection(user["user_id"]))
        keyboard.append([
            InlineKeyboardButton(
                f"👤 {name} ({hero_count} героев)", 
                callback_data=f"friends_add_from_list|{user['user_id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="friends_menu")])
    
    await query.edit_message_text(
        "👥 **Выбери игрока для добавления в друзья:**",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def friends_add_from_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    friend_id = int(query.data.split("|")[1])
    
    if user_id == friend_id:
        await query.edit_message_text("❌ Нельзя добавить самого себя!")
        return
    
    if is_friend(user_id, friend_id):
        await query.edit_message_text("✅ Этот пользователь уже в вашем списке друзей!")
        return
    
    if add_friend(user_id, friend_id):
        try:
            chat = await context.bot.get_chat(friend_id)
            name = chat.first_name or "Пользователь"
        except:
            name = f"ID {friend_id}"
        
        await query.edit_message_text(
            f"✅ *{name}* добавлен в список друзей!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="friends_menu")]])
        )
    else:
        await query.edit_message_text("❌ Ошибка при добавлении друга.")


async def handle_add_friend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get('waiting_for_friend_id'):
        return
    
    user_id = update.effective_user.id
    try:
        friend_id = int(update.message.text.strip())
        
        if friend_id == user_id:
            await update.message.reply_text("❌ Нельзя добавить самого себя!")
            context.user_data['waiting_for_friend_id'] = False
            return
        
        user = get_user_by_id(friend_id)
        if not user:
            await update.message.reply_text("❌ Пользователь с таким ID не найден!")
            context.user_data['waiting_for_friend_id'] = False
            return
        
        if is_friend(user_id, friend_id):
            await update.message.reply_text("✅ Этот пользователь уже в вашем списке друзей!")
            context.user_data['waiting_for_friend_id'] = False
            return
        
        if add_friend(user_id, friend_id):
            try:
                chat = await context.bot.get_chat(friend_id)
                name = chat.first_name or "Пользователь"
            except:
                name = f"ID {friend_id}"
            
            await update.message.reply_text(f"✅ *{name}* добавлен в список друзей!", parse_mode="Markdown")
            context.user_data['waiting_for_friend_id'] = False
            await friends_menu(update, context)
        else:
            await update.message.reply_text("❌ Ошибка при добавлении друга. Попробуйте позже.")
            
    except ValueError:
        await update.message.reply_text("❌ Некорректный ID. Введите число.")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name or "Пользователь"
    
    text = (
        f"🆔 **Ваш ID:** `{user_id}`\n\n"
        f"👤 Имя: {first_name}\n\n"
        "Отправьте этот ID другу, чтобы он мог добавить вас в друзья.\n"
        "Или используйте этот ID, чтобы добавить друга."
    )
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def report_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    
    text = (
        "📩 **Сообщить об ошибке**\n\n"
        "Если ты нашёл ошибку в боте или хочешь предложить идею, просто отправь сообщение с описанием проблемы.\n\n"
        "Спасибо за обратную связь!"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    
    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def forward_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user = update.effective_user
        user_name = user.first_name or "Пользователь"
        user_id = user.id
        
        message_text = (
            f"📩 Новое сообщение от пользователя\n\n"
            f"👤 Имя: {user_name}\n"
            f"🆔 ID: {user_id}\n\n"
            f"📝 Сообщение:\n{update.message.text}"
        )
        
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=message_text,
                parse_mode=None
            )
            await update.message.reply_text(
                "✅ Сообщение отправлено разработчику! Спасибо за обратную связь."
            )
        except Exception as e:
            print(f"❌ Ошибка отправки админу: {e}")
            await update.message.reply_text(
                "❌ Не удалось отправить сообщение. Попробуй позже."
            )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        try:
            await query.answer()
        except Exception:
            pass
        chat_id = query.message.chat_id
        is_photo = query.message.photo
    else:
        chat_id = update.effective_chat.id
        is_photo = False

    help_text = (
        "❓ **Список команд**\n\n"
        "/start — Главное меню\n"
        "/help — Эта справка\n"
        "/id — Показать свой ID\n"
        "/duel — Начать дуэль\n"
        "/stopduel — Завершить дуэль\n"
        "/quiz — Викторина\n"
        "/stopquiz — Завершить викторину\n"
        "/addcoins — (админ) Добавить монеты\n\n"
        "📌 **Как играть**\n"
        "1. Бесплатный пак каждые 3 часа.\n"
        "2. Покупай паки за монеты с лучшими шансами.\n"
        "3. Участвуй в дуэлях и зарабатывай монеты.\n"
        "4. Собирай альбом и готовься к ЕГЭ!\n"
        "5. Проходи викторину и получай бонусы!"
    )

    keyboard = [[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]]
    
    if query:
        if is_photo:
            try:
                await query.message.delete()
            except Exception:
                pass
            await context.bot.send_message(
                chat_id=chat_id,
                text=help_text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            try:
                await query.edit_message_text(
                    help_text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            except Exception:
                pass
    else:
        await update.message.reply_text(
            help_text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def show_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    user_id = query.from_user.id
    user = get_user(user_id)
    
    msg = f"💰 **Твой баланс:** {user['coins']} монет.\n\nЗарабатывай монеты, участвуя в дуэлях (победа +20, поражение -5) и открывая паки!"
    keyboard = [[InlineKeyboardButton("🔙 На главную", callback_data="main_menu")]]
    
    if query.message.photo:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        try:
            await query.edit_message_text(
                msg,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass


async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    try:
        await query.answer()
    except Exception:
        pass
    
    user_id = query.from_user.id
    user = get_user(user_id)
    
    keyboard = [
        [InlineKeyboardButton("📖 Дар читателя (бесплатно)", callback_data="free_pack")],
        [InlineKeyboardButton("📚 Маленький пак (200 монет)", callback_data="small_pack")],
        [InlineKeyboardButton("🔮 Лишний пак (500 монет)", callback_data="medium_pack")],
        [InlineKeyboardButton("✨ Новый пак (1000 монет)", callback_data="large_pack")],
        [InlineKeyboardButton("🔙 На главную", callback_data="main_menu")],
    ]
    
    msg = f"🛒 **Магазин паков**\n\n💰 Твой баланс: {user['coins']} монет\n\nВыбери, что хочешь открыть:"
    
    if query.message.photo:
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=msg,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        try:
            await query.edit_message_text(
                msg,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception:
            pass