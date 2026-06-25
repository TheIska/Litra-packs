from bot.handlers.album import show_card_by_number
from bot.models.hero import HEROES_BY_NUMBER

print("✅ Импорты работают")
print(f"📊 Всего героев: {len(HEROES_BY_NUMBER)}")

hero = HEROES_BY_NUMBER.get(6)
if hero:
    print(f"📌 Герой: {hero.get('name')}")
    print(f"📝 Описание: {hero.get('description', 'НЕТ!')}")