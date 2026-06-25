import json
from bot.database import get_connection
from bot.models.hero import HEROES_BY_NUMBER

def check_cards():
    print("=" * 60)
    print("🔍 ПРОВЕРКА КАРТ В БД")
    print("=" * 60)
    
    conn = get_connection()
    c = conn.cursor()
    
    # Получаем все карты
    c.execute("SELECT id, user_id, hero_key, hero_data, card_number FROM collection")
    cards = c.fetchall()
    
    if not cards:
        print("❌ Нет карт в БД!")
        conn.close()
        return
    
    print(f"\n📊 Найдено карт: {len(cards)}")
    print("-" * 60)
    
    for card_id, user_id, hero_key, hero_data, card_number in cards:
        hero = json.loads(hero_data)
        name = hero.get("name", "Неизвестный")
        description = hero.get("description", "НЕТ ОПИСАНИЯ")
        card_num = hero.get("card_number", 0)
        
        print(f"🆔 {card_id} | Пользователь: {user_id}")
        print(f"   Имя: {name}")
        print(f"   Номер: {card_num}")
        print(f"   Описание: {description[:50]}..." if len(description) > 50 else f"   Описание: {description}")
        print("-" * 60)
    
    conn.close()

if __name__ == "__main__":
    check_cards()