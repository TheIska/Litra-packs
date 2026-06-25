from bot.models.hero import HEROES_BY_NUMBER
from bot.database import get_collection
import os

# Тестируем получение описания для героя
def test_album():
    print("=" * 60)
    print("🔍 ТЕСТ АЛЬБОМА")
    print("=" * 60)
    
    # Берем героя №6 (Евгений Онегин)
    hero_info = HEROES_BY_NUMBER.get(6)
    
    print(f"\n📌 Герой из hero.py:")
    print(f"   Имя: {hero_info.get('name')}")
    print(f"   Описание: {hero_info.get('description', 'НЕТ!')[:100]}...")
    
    # Проверяем, что description точно есть
    description = hero_info.get("description")
    if description:
        print("\n✅ Описание есть в hero.py")
    else:
        print("\n❌ Описания НЕТ в hero.py")
    
    # Проверяем, как album.py берет описание
    print("\n" + "-" * 60)
    print("🔍 Как album.py берет описание:")
    print("   description = hero_info.get('description', 'ШАБЛОН')")
    print(f"   Результат: {hero_info.get('description', 'ШАБЛОН')[:50]}...")

if __name__ == "__main__":
    test_album()