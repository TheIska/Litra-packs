import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional, Any

DB_PATH = "bot_data.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
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
    """Добавляет героя в коллекцию пользователя"""
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