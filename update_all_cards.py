import json
from bot.database import get_connection
from bot.models.hero import HEROES_BY_NUMBER

def update_all_cards():
    print("=" * 60)
    print("🔄 ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ ВСЕХ КАРТ")
    print("=" * 60)
    
    conn = get_connection()
    c = conn.cursor()
    
    # Получаем все карты всех пользователей
    c.execute("SELECT id, user_id, hero_key, hero_data FROM collection")
    cards = c.fetchall()
    
    if not cards:
        print("ℹ️ Нет карт в коллекции. Сначала открой паки в боте!")
        conn.close()
        return
    
    total_updated = 0
    
    for card_id, user_id, hero_key, hero_data in cards:
        try:
            hero = json.loads(hero_data)
            hero_name = hero.get("name", "")
            
            # Ищем полные данные героя по имени
            found_hero = None
            found_number = None
            for num, h in HEROES_BY_NUMBER.items():
                if h.get("name") == hero_name:
                    found_hero = h
                    found_number = num
                    break
            
            if found_hero:
                # Обновляем все поля героя
                hero["card_number"] = found_number
                hero["description"] = found_hero.get("description", hero.get("description", "Описание отсутствует"))
                hero["strength"] = found_hero.get("strength", 50)
                hero["intelligence"] = found_hero.get("intelligence", 50)
                hero["kindness"] = found_hero.get("kindness", 50)
                hero["rarity"] = found_hero.get("rarity", "обычный")
                hero["author"] = found_hero.get("author", hero.get("author", "Неизвестный"))
                hero["book"] = found_hero.get("book", hero.get("book", "Неизвестное произведение"))
                
                new_hero_data = json.dumps(hero, ensure_ascii=False)
                
                c.execute(
                    "UPDATE collection SET hero_data = ?, card_number = ? WHERE id = ?",
                    (new_hero_data, found_number, card_id)
                )
                total_updated += 1
                print(f"   ✅ {hero_name} → №{found_number} (описание добавлено)")
            else:
                print(f"   ⚠️ Не найден герой: {hero_name}")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"📊 Обновлено карт: {total_updated}")
    print("✅ Готово!")

if __name__ == "__main__":
    update_all_cards()