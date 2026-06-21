# bot/fix_card_numbers.py
from database import get_connection
from models.hero import HEROES_BY_NUMBER

def fix_card_numbers():
    """Исправляет номера карт в базе данных"""
    conn = get_connection()
    c = conn.cursor()
    
    # Проверяем, есть ли карты без номеров
    c.execute("SELECT COUNT(*) FROM collection WHERE card_number = 0 OR card_number IS NULL")
    empty_count = c.fetchone()[0]
    
    if empty_count == 0:
        print("✅ Все карты уже имеют номера!")
        conn.close()
        return
    
    print(f"🔄 Найдено {empty_count} карт без номеров. Исправляем...")
    
    # Получаем всех пользователей
    c.execute("SELECT DISTINCT user_id FROM collection")
    users = c.fetchall()
    
    fixed = 0
    for user in users:
        user_id = user[0]
        c.execute("SELECT id, hero_key FROM collection WHERE user_id = ?", (user_id,))
        cards = c.fetchall()
        
        for card_id, hero_key in cards:
            # Находим героя по ключу
            found = False
            for number, hero in HEROES_BY_NUMBER.items():
                if f"{hero['author']} – {hero['name']}" == hero_key:
                    c.execute("UPDATE collection SET card_number = ? WHERE id = ?", (number, card_id))
                    fixed += 1
                    found = True
                    break
            
            if not found:
                print(f"⚠️ Не найден герой для: {hero_key}")
    
    conn.commit()
    conn.close()
    print(f"✅ Исправлено {fixed} карт!")

if __name__ == "__main__":
    fix_card_numbers()