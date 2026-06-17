from telegram import Update
from telegram.ext import ContextTypes
from ..database import add_coins, get_user

ADMIN_ID = 6082384471

async def add_coins_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("⛔ У тебя нет прав для этой команды.")
        return
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("❌ Используй: `/addcoins <количество>`", parse_mode="Markdown")
        return
    try:
        amount = int(context.args[0])
        if amount <= 0:
            await update.message.reply_text("❌ Сумма должна быть положительной.")
            return
    except ValueError:
        await update.message.reply_text("❌ Введи число.")
        return
    add_coins(user_id, amount)
    user = get_user(user_id)
    await update.message.reply_text(
        f"✅ Добавлено *{amount}* монет!\n💰 Новый баланс: *{user['coins']}* монет.",
        parse_mode="Markdown"
    )