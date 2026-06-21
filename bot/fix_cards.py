# bot/fix_cards.py
import json
from database import get_connection
from models.hero import HEROES_BY_NUMBER

def fix_card_numbers():
    """Исправляет номера карт в базе данных"""
    conn = get_connection()
    c = conn.cursor()
    
    # Проверяем, есть ли карты с номером 0
    c.execute("SELECT COUNT(*) FROM collection WHERE card_number = 0")
    zero_count = c.fetchone()[0]
    
    if zero_count == 0:
        print("✅ Все карты уже имеют правильные номера!")
        conn.close()
        return
    
    print(f"🔄 Найдено {zero_count} карт с номером 000. Исправляем...")
    
    # Получаем все карты с номером 0
    c.execute("SELECT id, hero_key, hero_data FROM collection WHERE card_number = 0")
    cards = c.fetchall()
    
    fixed = 0
    not_found = 0
    
    for card_id, hero_key, hero_data in cards:
        # Ищем героя по ключу
        found = False
        for number, hero in HEROES_BY_NUMBER.items():
            hero_key_from_dict = f"{hero['author']} – {hero['name']}"
            if hero_key_from_dict == hero_key:
                c.execute("UPDATE collection SET card_number = ? WHERE id = ?", (number, card_id))
                fixed += 1
                found = True
                break
        
        if not found:
            # Пробуем найти по имени в данных
            try:
                data = json.loads(hero_data)
                name = data.get('name', '')
                author = data.get('author', '')
                
                for number, hero in HEROES_BY_NUMBER.items():
                    if hero['name'] == name and hero['author'] == author:
                        c.execute("UPDATE collection SET card_number = ? WHERE id = ?", (number, card_id))
                        fixed += 1
                        found = True
                        break
            except:
                pass
        
        if not found:
            not_found += 1
            print(f"⚠️ Не найден герой для: {hero_key}")
    
    conn.commit()
    conn.close()
    print(f"✅ Исправлено {fixed} карт")
    if not_found > 0:
        print(f"⚠️ Не найдено {not_found} карт")

if __name__ == "__main__":
    fix_card_numbers()