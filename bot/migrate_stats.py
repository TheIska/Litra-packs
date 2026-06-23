# bot/migrate_stats.py
from database import get_connection
from models.hero import HEROES_BY_NUMBER
import json
import random

def migrate_stats():
    """Добавляет характеристики старым картам в базе данных"""
    print("🔄 Запуск миграции характеристик...")
    
    conn = get_connection()
    c = conn.cursor()
    
    # Проверяем, есть ли колонка card_number
    c.execute("PRAGMA table_info(collection)")
    columns = [col[1] for col in c.fetchall()]
    
    if "card_number" not in columns:
        print("❌ Колонка card_number не найдена! Запустите migrate_db()")
        return
    
    # Получаем все карты
    c.execute("SELECT id, hero_data, card_number FROM collection")
    rows = c.fetchall()
    
    if not rows:
        print("📭 В базе нет карт")
        return
    
    print(f"📊 Найдено {len(rows)} карт")
    
    fixed = 0
    not_found = 0
    
    for card_id, hero_data, card_number in rows:
        try:
            hero = json.loads(hero_data)
            
            # Проверяем, есть ли характеристики
            if "strength" not in hero or "intelligence" not in hero or "kindness" not in hero:
                # Ищем героя в эталонном словаре по номеру
                if card_number in HEROES_BY_NUMBER:
                    ref = HEROES_BY_NUMBER[card_number]
                    hero["strength"] = ref["strength"]
                    hero["intelligence"] = ref["intelligence"]
                    hero["kindness"] = ref["kindness"]
                    fixed += 1
                else:
                    # Если не нашли - генерируем случайные
                    hero["strength"] = random.randint(30, 80)
                    hero["intelligence"] = random.randint(30, 80)
                    hero["kindness"] = random.randint(30, 80)
                    not_found += 1
                    fixed += 1
                
                # Обновляем запись в БД
                c.execute(
                    "UPDATE collection SET hero_data = ? WHERE id = ?",
                    (json.dumps(hero, ensure_ascii=False), card_id)
                )
                
        except Exception as e:
            print(f"❌ Ошибка при обработке карты {card_id}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Обновлено {fixed} карт")
    if not_found > 0:
        print(f"⚠️ Для {not_found} карт использованы случайные значения")
    print("✅ Миграция завершена!")

if __name__ == "__main__":
    migrate_stats()