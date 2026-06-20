# bot/migrate_cards.py
import sqlite3
import os
from database import get_connection

def migrate_card_numbers():
    """Присваивает номера существующим картам в коллекции"""
    conn = get_connection()
    c = conn.cursor()
    
    # Проверяем наличие колонки card_number
    c.execute("PRAGMA table_info(collection)")
    columns = [col[1] for col in c.fetchall()]
    
    if "card_number" not in columns:
        print("❌ Колонка card_number не найдена! Запустите migrate_db()")
        return
    
    # Получаем всех пользователей у которых есть карты
    c.execute("SELECT DISTINCT user_id FROM collection")
    users = c.fetchall()
    
    if not users:
        print("📭 Нет карт в базе данных")
        return
    
    migrated = 0
    for user in users:
        user_id = user[0]
        # Получаем все карты пользователя по дате получения
        c.execute("""
            SELECT id FROM collection 
            WHERE user_id = ? 
            ORDER BY obtained_at, id
        """, (user_id,))
        cards = c.fetchall()
        
        # Присваиваем номера по порядку
        for i, card in enumerate(cards, 1):
            c.execute("""
                UPDATE collection 
                SET card_number = ? 
                WHERE id = ?
            """, (i, card[0]))
            migrated += 1
        
        print(f"👤 Пользователь {user_id}: {len(cards)} карт")
    
    conn.commit()
    conn.close()
    print(f"\n✅ Готово! Присвоены номера для {len(users)} пользователей, {migrated} карт")

if __name__ == "__main__":
    print("🔄 Запуск миграции номеров карт...")
    migrate_card_numbers()