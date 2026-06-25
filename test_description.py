from bot.models.hero import HEROES_BY_NUMBER, get_hero_by_name

# Проверяем героя по номеру 6 (Евгений Онегин)
print("=" * 60)
print("🔍 ПРОВЕРКА ОПИСАНИЙ В hero.py")
print("=" * 60)

# Проверяем по номеру
hero = HEROES_BY_NUMBER.get(6)
if hero:
    print(f"\n📌 Герой: {hero.get('name')}")
    print(f"📖 Книга: {hero.get('book')}")
    print(f"📝 Описание: {hero.get('description', 'ОПИСАНИЯ НЕТ!')}")
    print(f"   Длина описания: {len(hero.get('description', ''))} символов")
else:
    print("❌ Герой с номером 6 не найден")

# Проверяем по имени
print("\n" + "-" * 60)
hero2 = get_hero_by_name("Евгений Онегин")
if hero2:
    print(f"\n📌 Поиск по имени: {hero2.get('name')}")
    print(f"📝 Описание: {hero2.get('description', 'ОПИСАНИЯ НЕТ!')}")
else:
    print("❌ Герой с именем 'Евгений Онегин' не найден")

# Считаем, у скольких героев есть описания
print("\n" + "-" * 60)
count = 0
for num, h in HEROES_BY_NUMBER.items():
    if h.get('description'):
        count += 1
print(f"📊 Всего героев: {len(HEROES_BY_NUMBER)}")
print(f"📊 С описанием: {count}")
print(f"📊 Без описания: {len(HEROES_BY_NUMBER) - count}")

# Покажем пример описания
print("\n" + "-" * 60)
if count > 0:
    for num, h in HEROES_BY_NUMBER.items():
        if h.get('description'):
            print(f"✅ Пример описания для {h.get('name')}:")
            print(f"   {h.get('description')[:100]}...")
            break