import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .config import BOT_TOKEN
from .database import init_db
from .handlers.start import start, help_command
from .handlers.pack import free_pack
from .handlers.collection import show_collection
from .handlers.duel import (
    duel_command,
    card_selection_callback,
    answer_callback
)
from .web.server import keep_alive

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    # Инициализация базы данных
    init_db()
    
    # Запуск Flask-сервера для keep-alive (чтобы бот не засыпал)
    keep_alive()
    
    # Создание приложения
    app = Application.builder().token(BOT_TOKEN).build()

    # ========== РЕГИСТРАЦИЯ КОМАНД ==========
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("duel", duel_command))

    # ========== РЕГИСТРАЦИЯ CALLBACK-ЗАПРОСОВ ==========
    # Главное меню
    app.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
    
    # Открытие пака и коллекция
    app.add_handler(CallbackQueryHandler(free_pack, pattern="^free_pack$"))
    app.add_handler(CallbackQueryHandler(show_collection, pattern="^collection$"))
    
    # Дуэли
    app.add_handler(CallbackQueryHandler(duel_command, pattern="^duel$"))
    app.add_handler(CallbackQueryHandler(card_selection_callback, pattern="^duel_card_"))
    app.add_handler(CallbackQueryHandler(card_selection_callback, pattern="^duel_ready_"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^duel_answer_"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^duel_bonus_"))

    # ========== ЗАПУСК БОТА ==========
    print("🤖 Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()