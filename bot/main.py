# bot/main.py

import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from .config import BOT_TOKEN
from .database import init_db, migrate_db
from .handlers.start import (
    start, 
    help_command, 
    show_coins, 
    shop, 
    report_error, 
    forward_to_admin
)
from .handlers.pack import free_pack, small_pack, medium_pack, large_pack
from .handlers.album import (
    show_album, 
    album_navigation, 
    show_card_by_number,
    album_back
)
from .handlers.duel import (
    duel_command,
    answer_callback,
    stop_duel_command,
    handle_hero_selection,
    handle_invite_link,
    duel_random,
    duel_friend,
    duel_friend_select,
    duel_bot,
    duel_accept,
    duel_decline,
    duel_invite,
    copy_link,
    share_link,
)
from .handlers.admin import add_coins_command
from .handlers.quiz import quiz_command, quiz_answer_callback, stop_quiz_command
from .web.server import keep_alive

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    init_db()
    migrate_db()
    keep_alive()

    app = Application.builder().token(BOT_TOKEN).build()

    # ========== КОМАНДЫ ==========
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("start", handle_invite_link))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("duel", duel_command))
    app.add_handler(CommandHandler("stopduel", stop_duel_command))
    app.add_handler(CommandHandler("addcoins", add_coins_command))
    app.add_handler(CommandHandler("quiz", quiz_command))
    app.add_handler(CommandHandler("stopquiz", stop_quiz_command))

    # ========== CALLBACK'И МЕНЮ ==========
    app.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(shop, pattern="^shop$"))
    app.add_handler(CallbackQueryHandler(show_coins, pattern="^coins$"))
    app.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(quiz_command, pattern="^quiz$"))
    app.add_handler(CallbackQueryHandler(report_error, pattern="^report_error$"))

    # ========== ПАКИ ==========
    app.add_handler(CallbackQueryHandler(free_pack, pattern="^free_pack$"))
    app.add_handler(CallbackQueryHandler(small_pack, pattern="^small_pack$"))
    app.add_handler(CallbackQueryHandler(medium_pack, pattern="^medium_pack$"))
    app.add_handler(CallbackQueryHandler(large_pack, pattern="^large_pack$"))

    # ========== АЛЬБОМ ==========
    app.add_handler(CallbackQueryHandler(show_card_by_number, pattern="^album_card_"))
    app.add_handler(CallbackQueryHandler(album_back, pattern="^album_back$"))
    app.add_handler(CallbackQueryHandler(album_navigation, pattern="^album_"))
    app.add_handler(CallbackQueryHandler(show_album, pattern="^album$"))

    # ========== ДУЭЛИ ==========
    app.add_handler(CallbackQueryHandler(duel_command, pattern="^duel$"))
    app.add_handler(CallbackQueryHandler(duel_random, pattern="^duel_random$"))
    app.add_handler(CallbackQueryHandler(duel_friend, pattern="^duel_friend$"))
    app.add_handler(CallbackQueryHandler(duel_friend_select, pattern="^duel_friend_select\|"))
    app.add_handler(CallbackQueryHandler(duel_bot, pattern="^duel_bot$"))
    app.add_handler(CallbackQueryHandler(duel_accept, pattern="^duel_accept\|"))
    app.add_handler(CallbackQueryHandler(duel_decline, pattern="^duel_decline$"))
    app.add_handler(CallbackQueryHandler(duel_invite, pattern="^duel_invite$"))
    app.add_handler(CallbackQueryHandler(copy_link, pattern="^copy_link\|"))
    app.add_handler(CallbackQueryHandler(share_link, pattern="^share_link\|"))
    
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^ans\|"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^b\|"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^s\|"))
    
    # ========== ВЫБОР ГЕРОЕВ ==========
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^hsel\|"))
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^hpage\|"))
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^startduel$"))
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^noop$"))

    # ========== ВИКТОРИНА ==========
    app.add_handler(CallbackQueryHandler(quiz_answer_callback, pattern="^qans\|"))

    # ========== ПЕРЕСЫЛКА СООБЩЕНИЙ АДМИНУ ==========
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))

    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()