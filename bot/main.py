import logging
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from .config import BOT_TOKEN
from .database import init_db, migrate_db
from .handlers.start import (
    start, 
    help_command, 
    show_coins, 
    shop, 
    report_error, 
    forward_to_admin,
    id_command,
    friends_menu,
    friends_add_id,
    friends_from_list,
    friends_add_from_list,
    handle_add_friend,
)
from .handlers.pack import free_pack, small_pack, medium_pack, large_pack
from .handlers.album import (
    show_album, 
    album_navigation, 
    show_card_by_number,
    album_back,
    sell_duplicates_menu,
    sell_duplicates_card,
    sell_duplicates_confirm,
    sell_duplicates_all,
    sell_duplicates_all_confirm,
)
from .handlers.duel import (
    duel_command,
    answer_callback,
    stop_duel_command,
    handle_hero_selection,
    duel_friends,
    duel_friend_select,
    duel_bot,
    duel_accept,
    duel_decline,
)
from .handlers.admin import add_coins_command
from .handlers.quiz import quiz_command, quiz_answer_callback, stop_quiz_command

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    init_db()
    migrate_db()

    # ========== НАСТРОЙКА ПРОКСИ ==========
    # Раскомментируй нужную строку и вставь свои данные
    
    # Для SOCKS5 прокси (например, Tor)
    # proxy_url = "socks5://127.0.0.1:9050"
    
    # Для HTTP/HTTPS прокси
    # proxy_url = "http://user:pass@proxy_ip:port"
    # proxy_url = "http://proxy_ip:port"
    
    # Или из переменных окружения
    # proxy_url = os.getenv("PROXY_URL")

    # Создаём приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Применяем прокси (если указан)
    # if proxy_url:
    #     app.bot.request = app.bot.request.with_proxy(proxy_url)
    #     print(f"✅ Прокси настроен: {proxy_url}")

    # ========== КОМАНДЫ ==========
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("id", id_command))
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

    # ========== ПРОДАЖА ДУБЛИКАТОВ ==========
    app.add_handler(CallbackQueryHandler(sell_duplicates_menu, pattern="sell_duplicates_menu"))
    app.add_handler(CallbackQueryHandler(sell_duplicates_card, pattern="sell_duplicates_card"))
    app.add_handler(CallbackQueryHandler(sell_duplicates_confirm, pattern="sell_duplicates_confirm"))
    app.add_handler(CallbackQueryHandler(sell_duplicates_all, pattern="sell_duplicates_all"))
    app.add_handler(CallbackQueryHandler(sell_duplicates_all_confirm, pattern="sell_duplicates_all_confirm"))

    # ========== ДРУЗЬЯ ==========
    app.add_handler(CallbackQueryHandler(friends_menu, pattern="^friends_menu$"))
    app.add_handler(CallbackQueryHandler(friends_add_id, pattern="^friends_add_id$"))
    app.add_handler(CallbackQueryHandler(friends_from_list, pattern="^friends_from_list$"))
    app.add_handler(CallbackQueryHandler(friends_add_from_list, pattern="^friends_add_from_list\\|"))

    # ========== ДУЭЛИ ==========
    app.add_handler(CallbackQueryHandler(duel_command, pattern="^duel$"))
    app.add_handler(CallbackQueryHandler(duel_friends, pattern="^duel_friends$"))
    app.add_handler(CallbackQueryHandler(duel_friend_select, pattern="^duel_friend_select\\|"))
    app.add_handler(CallbackQueryHandler(duel_bot, pattern="^duel_bot$"))
    app.add_handler(CallbackQueryHandler(duel_accept, pattern="^duel_accept\\|"))
    app.add_handler(CallbackQueryHandler(duel_decline, pattern="^duel_decline$"))
    
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^ans\\|"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^b\\|"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^f\\|"))
    
    # ========== ВЫБОР ГЕРОЕВ ==========
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^hsel\\|"))
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^hpage\\|"))
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^startduel$"))
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(handle_hero_selection, pattern="^noop$"))

    # ========== ВИКТОРИНА ==========
    app.add_handler(CallbackQueryHandler(quiz_answer_callback, pattern="^qans_"))
    app.add_handler(CallbackQueryHandler(stop_quiz_command, pattern="^stop_quiz$"))

    # ========== ВВОД ДЛЯ ДРУЗЕЙ ==========
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_friend))

    # ========== ПЕРЕСЫЛКА СООБЩЕНИЙ АДМИНУ ==========
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_admin))

    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()