# bot/handlers/__init__.py
from .start import start, help_command, show_coins, shop
from .pack import free_pack, small_pack, medium_pack, large_pack
from .collection import show_collection
from .duel import (
    duel_command,
    answer_callback,
    stop_duel_command,
    handle_hero_selection  # Добавляем
)
from .admin import add_coins_command