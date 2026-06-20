import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

# База данных в папке data/
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'bot_data.db')

def get_connection():
    """Возвращает соединение с базой данных"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Создаёт таблицы, если их нет"""
    conn = get_connection()
    c = conn.cursor()
    
    # Таблица пользователей
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            last_free_pack TIMESTAMP,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            rating INTEGER DEFAULT 1200,
            coins INTEGER DEFAULT 500,
            daily_quiz_streak INTEGER DEFAULT 0,
            daily_quiz_last_date TEXT,
            daily_quiz_done INTEGER DEFAULT 0
        )
    ''')
    
    # Таблица коллекции героев
    c.execute('''
        CREATE TABLE IF NOT EXISTS collection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            hero_key TEXT,
            hero_data TEXT,
            obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            UNIQUE(user_id, hero_key)
        )
    ''')
    
    conn.commit()
    conn.close()

def migrate_db():
    """Добавляет недостающие колонки для викторины"""
    conn = get_connection()
    c = conn.cursor()
    
    # Проверяем существующие колонки
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    
    if "daily_quiz_streak" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN daily_quiz_streak INTEGER DEFAULT 0")
        print("✅ Добавлена колонка daily_quiz_streak")
    
    if "daily_quiz_last_date" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN daily_quiz_last_date TEXT")
        print("✅ Добавлена колонка daily_quiz_last_date")
    
    if "daily_quiz_done" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN daily_quiz_done INTEGER DEFAULT 0")
        print("✅ Добавлена колонка daily_quiz_done")
    
    conn.commit()
    conn.close()

def get_user(user_id: int) -> Dict[str, Any]:
    """Возвращает данные пользователя с автоматической миграцией"""
    conn = get_connection()
    c = conn.cursor()
    
    # Проверяем и добавляем недостающие колонки
    c.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in c.fetchall()]
    
    if "daily_quiz_streak" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN daily_quiz_streak INTEGER DEFAULT 0")
    if "daily_quiz_last_date" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN daily_quiz_last_date TEXT")
    if "daily_quiz_done" not in columns:
        c.execute("ALTER TABLE users ADD COLUMN daily_quiz_done INTEGER DEFAULT 0")
    
    c.execute("""
        SELECT last_free_pack, wins, losses, rating, coins, 
               daily_quiz_streak, daily_quiz_last_date, daily_quiz_done 
        FROM users WHERE user_id = ?
    """, (user_id,))
    row = c.fetchone()
    
    if row:
        result = {
            "user_id": user_id,
            "last_free_pack": row[0],
            "wins": row[1] or 0,
            "losses": row[2] or 0,
            "rating": row[3] or 1200,
            "coins": row[4] or 500,
            "daily_quiz_streak": row[5] or 0,
            "daily_quiz_last_date": row[6],
            "daily_quiz_done": row[7] or 0,
        }
    else:
        c.execute("INSERT INTO users (user_id, coins) VALUES (?, 500)", (user_id,))
        conn.commit()
        result = {
            "user_id": user_id,
            "last_free_pack": None,
            "wins": 0,
            "losses": 0,
            "rating": 1200,
            "coins": 500,
            "daily_quiz_streak": 0,
            "daily_quiz_last_date": None,
            "daily_quiz_done": 0,
        }
    
    conn.commit()
    conn.close()
    return result

def update_user(user_id: int, **kwargs) -> None:
    """Обновляет поля пользователя"""
    if not kwargs:
        return
    
    conn = get_connection()
    c = conn.cursor()
    fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [user_id]
    c.execute(f"UPDATE users SET {fields} WHERE user_id = ?", values)
    conn.commit()
    conn.close()

def get_collection(user_id: int) -> Dict[str, Dict]:
    """Возвращает коллекцию героев пользователя"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT hero_key, hero_data FROM collection WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    result = {}
    for key, data in rows:
        result[key] = json.loads(data)
    conn.close()
    return result

def add_hero_to_collection(user_id: int, hero: Dict) -> None:
    """Добавляет героя в коллекцию"""
    hero_key = f"{hero['author']} – {hero['name']}"
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO collection (user_id, hero_key, hero_data) VALUES (?, ?, ?)",
        (user_id, hero_key, json.dumps(hero, ensure_ascii=False))
    )
    conn.commit()
    conn.close()

def update_last_free_pack(user_id: int, timestamp: datetime) -> None:
    """Обновляет время последнего бесплатного пака"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET last_free_pack = ? WHERE user_id = ?", (timestamp.isoformat(), user_id))
    conn.commit()
    conn.close()

def update_duel_stats(user_id: int, win: bool) -> None:
    """Обновляет статистику дуэлей"""
    conn = get_connection()
    c = conn.cursor()
    if win:
        c.execute("UPDATE users SET wins = wins + 1, rating = rating + 10 WHERE user_id = ?", (user_id,))
    else:
        c.execute("UPDATE users SET losses = losses + 1, rating = rating - 5 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_opponent(user_id: int) -> Optional[int]:
    """Находит случайного соперника для дуэли"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id != ? ORDER BY RANDOM() LIMIT 1", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_all_users() -> list:
    """Возвращает список всех пользователей"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [{"user_id": row[0]} for row in rows]

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Возвращает данные пользователя по ID"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT user_id, last_free_pack, wins, losses, rating, coins,
               daily_quiz_streak, daily_quiz_last_date, daily_quiz_done 
        FROM users WHERE user_id = ?
    """, (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "last_free_pack": row[1],
            "wins": row[2] or 0,
            "losses": row[3] or 0,
            "rating": row[4] or 1200,
            "coins": row[5] or 500,
            "daily_quiz_streak": row[6] or 0,
            "daily_quiz_last_date": row[7],
            "daily_quiz_done": row[8] or 0,
        }
    return None

def add_coins(user_id: int, amount: int) -> None:
    """Добавляет монеты пользователю"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def spend_coins(user_id: int, amount: int) -> bool:
    """Списывает монеты, возвращает True если успешно"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT coins FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row and row[0] >= amount:
        c.execute("UPDATE users SET coins = coins - ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def get_leaderboard(limit: int = 10) -> list:
    """Возвращает топ игроков по рейтингу"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT user_id, wins, losses, rating, coins 
        FROM users 
        ORDER BY rating DESC 
        LIMIT ?
    """, (limit,))
    rows = c.fetchall()
    conn.close()
    return [
        {
            "user_id": row[0],
            "wins": row[1] or 0,
            "losses": row[2] or 0,
            "rating": row[3] or 1200,
            "coins": row[4] or 500,
        }
        for row in rows
    ]

def get_user_stats(user_id: int) -> Dict[str, Any]:
    """Возвращает статистику пользователя"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT wins, losses, rating, coins FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "wins": row[0] or 0,
            "losses": row[1] or 0,
            "rating": row[2] or 1200,
            "coins": row[3] or 500,
        }
    return {"wins": 0, "losses": 0, "rating": 1200, "coins": 500}

def get_collection_count(user_id: int) -> int:
    """Возвращает количество героев в коллекции"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM collection WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_heroes_by_rarity(user_id: int) -> Dict[str, int]:
    """Возвращает количество героев по редкости"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT hero_data FROM collection WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    
    result = {"легендарный": 0, "эпический": 0, "редкий": 0, "обычный": 0}
    for row in rows:
        try:
            hero = json.loads(row[0])
            rarity = hero.get("rarity", "обычный")
            if rarity in result:
                result[rarity] += 1
        except:
            pass
    return result

def get_daily_quiz_status(user_id: int) -> Dict[str, Any]:
    """Возвращает статус ежедневной викторины"""
    user = get_user(user_id)
    return {
        "streak": user.get("daily_quiz_streak", 0),
        "last_date": user.get("daily_quiz_last_date"),
        "done": user.get("daily_quiz_done", 0) == 1,
    }

def reset_daily_quiz(user_id: int) -> None:
    """Сбрасывает статус викторины (для тестов)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE users 
        SET daily_quiz_streak = 0, daily_quiz_last_date = NULL, daily_quiz_done = 0 
        WHERE user_id = ?
    """, (user_id,))
    conn.commit()
    conn.close()

def reset_user_data(user_id: int) -> None:
    """Сбрасывает все данные пользователя (для отладки)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM collection WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()