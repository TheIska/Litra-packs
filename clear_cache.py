import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'bot_data.db')

def clear_descriptions():
    print("🔄 Очистка кеша описаний...")
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Проверяем, есть ли таблица
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hero_descriptions'")
    if c.fetchone():
        # Удаляем все описания
        c.execute("DELETE FROM hero_descriptions")
        conn.commit()
        print("✅ Все описания удалены из кеша!")
        print("📝 Теперь бот будет генерировать их заново через GigaChat")
    else:
        print("ℹ️ Таблица hero_descriptions не найдена, ничего не удалено")
    
    conn.close()

if __name__ == "__main__":
    clear_descriptions()