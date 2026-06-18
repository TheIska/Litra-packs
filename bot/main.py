import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from .config import BOT_TOKEN
from .database import init_db
from .handlers.start import start, help_command, show_coins, shop
from .handlers.pack import free_pack, small_pack, medium_pack, large_pack
from .handlers.collection import show_collection
from .handlers.duel import (
    duel_command,
    selection_callback,
    answer_callback
)
from .handlers.admin import add_coins_command
from .web.server import keep_alive

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

def main():
    init_db()
    keep_alive()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("duel", duel_command))
    app.add_handler(CommandHandler("addcoins", add_coins_command))

    app.add_handler(CallbackQueryHandler(start, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(shop, pattern="^shop$"))
    app.add_handler(CallbackQueryHandler(show_coins, pattern="^coins$"))

    app.add_handler(CallbackQueryHandler(free_pack, pattern="^free_pack$"))
    app.add_handler(CallbackQueryHandler(small_pack, pattern="^small_pack$"))
    app.add_handler(CallbackQueryHandler(medium_pack, pattern="^medium_pack$"))
    app.add_handler(CallbackQueryHandler(large_pack, pattern="^large_pack$"))

    app.add_handler(CallbackQueryHandler(show_collection, pattern="^collection$"))

    # Дуэли
    app.add_handler(CallbackQueryHandler(duel_command, pattern="^duel$"))
    app.add_handler(CallbackQueryHandler(selection_callback, pattern="^sel_"))
    app.add_handler(CallbackQueryHandler(selection_callback, pattern="^nav_"))
    app.add_handler(CallbackQueryHandler(selection_callback, pattern="^rdy_"))
    app.add_handler(CallbackQueryHandler(selection_callback, pattern="^rst_"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^ans_"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^bon_"))
    app.add_handler(CallbackQueryHandler(answer_callback, pattern="^sur_"))

    print("🤖 Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()