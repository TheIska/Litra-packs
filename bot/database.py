import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, Optional, Any

# База данных теперь в папке data/
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'bot_data.db')

def get_connection():
    """Возвращает соединение с базой данных"""
    # Создаём папку data/, если её нет
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Создаёт таблицы, если их нет"""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            last_free_pack TIMESTAMP,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            rating INTEGER DEFAULT 1200,
            coins INTEGER DEFAULT 500
        )
    ''')
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

def get_user(user_id: int) -> Dict[str, Any]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT last_free_pack, wins, losses, rating, coins FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    if row:
        result = {
            "user_id": user_id,
            "last_free_pack": row[0],
            "wins": row[1],
            "losses": row[2],
            "rating": row[3],
            "coins": row[4]
        }
    else:
        c.execute("INSERT INTO users (user_id, coins) VALUES (?, 500)", (user_id,))
        conn.commit()
        result = {"user_id": user_id, "last_free_pack": None, "wins": 0, "losses": 0, "rating": 1200, "coins": 500}
    conn.close()
    return result

def get_collection(user_id: int) -> Dict[str, Dict]:
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
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET last_free_pack = ? WHERE user_id = ?", (timestamp.isoformat(), user_id))
    conn.commit()
    conn.close()

def update_duel_stats(user_id: int, win: bool) -> None:
    conn = get_connection()
    c = conn.cursor()
    if win:
        c.execute("UPDATE users SET wins = wins + 1, rating = rating + 10 WHERE user_id = ?", (user_id,))
    else:
        c.execute("UPDATE users SET losses = losses + 1, rating = rating - 5 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_opponent(user_id: int) -> Optional[int]:
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
    c.execute("SELECT user_id, last_free_pack, wins, losses, rating, coins FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "user_id": row[0],
            "last_free_pack": row[1],
            "wins": row[2],
            "losses": row[3],
            "rating": row[4],
            "coins": row[5]
        }
    return None

def add_coins(user_id: int, amount: int) -> None:
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def spend_coins(user_id: int, amount: int) -> bool:
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
    """Возвращает список лучших игроков по рейтингу"""
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
            "wins": row[1],
            "losses": row[2],
            "rating": row[3],
            "coins": row[4]
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
            "wins": row[0],
            "losses": row[1],
            "rating": row[2],
            "coins": row[3]
        }
    return {"wins": 0, "losses": 0, "rating": 1200, "coins": 500}

def get_collection_count(user_id: int) -> int:
    """Возвращает количество героев в коллекции пользователя"""
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

def reset_user_data(user_id: int) -> None:
    """Сбрасывает данные пользователя (для отладки)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM collection WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()