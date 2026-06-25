import json
from bot.database import get_connection
from bot.models.hero import HEROES_BY_NUMBER

def fix_cards():
    print("=" * 60)
    print("🔄 ОБНОВЛЕНИЕ КАРТ В БД")
    print("=" * 60)
    
    conn = get_connection()
    c = conn.cursor()
    
    # Получаем всех пользователей
    c.execute("SELECT DISTINCT user_id FROM collection")
    users = c.fetchall()
    
    if not users:
        print("ℹ️ Нет карт в коллекции")
        conn.close()
        return
    
    total_updated = 0
    
    for user in users:
        user_id = user[0]
        print(f"\n👤 Пользователь {user_id}:")
        
        # Получаем все карты пользователя
        c.execute("SELECT id, hero_key, hero_data, card_number FROM collection WHERE user_id = ?", (user_id,))
        cards = c.fetchall()
        
        for card_id, hero_key, hero_data, card_number in cards:
            try:
                hero = json.loads(hero_data)
                hero_name = hero.get("name", "")
                
                # Если card_number уже есть — пропускаем
                if card_number and card_number > 0:
                    print(f"   ⏭️ {hero_name} → уже есть №{card_number}")
                    continue
                
                # Ищем номер карты по имени
                found_number = None
                for num, h in HEROES_BY_NUMBER.items():
                    if h.get("name") == hero_name:
                        found_number = num
                        break
                
                if found_number:
                    # Обновляем hero_data с card_number
                    hero["card_number"] = found_number
                    new_hero_data = json.dumps(hero, ensure_ascii=False)
                    
                    c.execute(
                        "UPDATE collection SET hero_data = ?, card_number = ? WHERE id = ?",
                        (new_hero_data, found_number, card_id)
                    )
                    total_updated += 1
                    print(f"   ✅ {hero_name} → №{found_number}")
                else:
                    print(f"   ⚠️ Не найден номер для {hero_name}")
                    
            except Exception as e:
                print(f"   ❌ Ошибка: {e}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"📊 Обновлено карт: {total_updated}")
    print("✅ Готово!")

if __name__ == "__main__":
    fix_cards()