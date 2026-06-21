# bot/handlers/__init__.py

from .start import start, help_command, show_coins, shop, report_error, forward_to_admin
from .pack import free_pack, small_pack, medium_pack, large_pack
from .album import show_album, album_navigation, show_card_by_number, album_back
from .duel import (
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
    share_link
)
from .admin import add_coins_command
from .quiz import quiz_command, quiz_answer_callback, stop_quiz_command