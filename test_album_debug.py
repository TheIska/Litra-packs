from bot.models.hero import HEROES_BY_NUMBER
from bot.database import get_collection

# Проверяем героя №6
hero_info = HEROES_BY_NUMBER.get(6)

print("=" * 60)
print("🔍 ДЕБАГ АЛЬБОМА")
print("=" * 60)

print(f"\n📌 Герой из hero.py:")
print(f"   Имя: {hero_info.get('name')}")
print(f"   Описание: {hero_info.get('description', 'НЕТ!')[:80]}...")

# Проверяем, что лежит в БД для этого героя
collection = get_collection(123456789)  # Твой user_id подставь

print("\n📌 Проверка collection:")
print(f"   Всего карт в коллекции: {len(collection)}")

# Ищем карту с номером 6
card = None
for hero in collection.values():
    if hero.get('card_number') == 6:
        card = hero
        break

if card:
    print(f"   Карта №6 найдена: {card.get('name')}")
    print(f"   Описание из БД: {card.get('description', 'НЕТ ОПИСАНИЯ В БД')}")
else:
    print("   Карта №6 НЕ найдена в коллекции")