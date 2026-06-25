from bot.models.hero import HEROES_BY_NUMBER

# Проверяем героя №6
hero = HEROES_BY_NUMBER.get(6)
print(f"Имя: {hero.get('name')}")
print(f"Описание: {hero.get('description', 'НЕТ ОПИСАНИЯ!')}")
print(f"Ключ description есть: {'description' in hero}")