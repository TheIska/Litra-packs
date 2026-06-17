import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional, Any

DB_PATH = "bot_data.db"

def get_connection() -> sqlite3.Connection:
    """Возвращает соединение с базой данных"""
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
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
            rating INTEGER DEFAULT 1200
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

def get_user(user_id: int) -> Dict[str, Any]:
    """Получить данные пользователя или создать нового"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT last_free_pack, wins, losses, rating FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    
    if row:
        result = {
            "user_id": user_id,
            "last_free_pack": row[0],
            "wins": row[1],
            "losses": row[2],
            "rating": row[3]
        }
    else:
        c.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        result = {"user_id": user_id, "last_free_pack": None, "wins": 0, "losses": 0, "rating": 1200}
    
    conn.close()
    return result

def get_collection(user_id: int) -> Dict[str, Dict]:
    """Получить коллекцию героев пользователя"""
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
    """Добавить героя в коллекцию"""
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
    """Обновить время последнего открытия бесплатного пака"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET last_free_pack = ? WHERE user_id = ?", (timestamp.isoformat(), user_id))
    conn.commit()
    conn.close()

def update_duel_stats(user_id: int, win: bool) -> None:
    """Обновить статистику дуэлей (победа/поражение и рейтинг)"""
    conn = get_connection()
    c = conn.cursor()
    if win:
        c.execute("UPDATE users SET wins = wins + 1, rating = rating + 10 WHERE user_id = ?", (user_id,))
    else:
        c.execute("UPDATE users SET losses = losses + 1, rating = rating - 5 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_opponent(user_id: int) -> Optional[int]:
    """Найти случайного соперника для дуэли (исключая себя)"""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE user_id != ? ORDER BY RANDOM() LIMIT 1", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None