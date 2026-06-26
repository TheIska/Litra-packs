import sqlite3
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'bot_data.db')

def get_connection():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return sqlite3.connect(DB_PATH, timeout=30)

def with_retry(func, max_retries=5, delay=0.5):
    """Выполняет функцию с повторными попытками при блокировке БД"""
    for attempt in range(max_retries):
        try:
            return func()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))
                continue
            raise e

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
            coins INTEGER DEFAULT 500,
            daily_quiz_streak INTEGER DEFAULT 0,
            daily_quiz_last_date TEXT,
            daily_quiz_done INTEGER DEFAULT 0
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS collection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            hero_key TEXT,
            hero_data TEXT,
            obtained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            card_number INTEGER DEFAULT 0,
            duplicates INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            UNIQUE(user_id, hero_key)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            user_id INTEGER,
            friend_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, friend_id),
            FOREIGN KEY(user_id) REFERENCES users(user_id),
            FOREIGN KEY(friend_id) REFERENCES users(user_id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS hero_descriptions (
            hero_key TEXT PRIMARY KEY,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ База данных инициализирована: {DB_PATH}")

def migrate_db():
    conn = get_connection()
    c = conn.cursor()
    
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
    
    c.execute("PRAGMA table_info(collection)")
    collection_columns = [col[1] for col in c.fetchall()]
    
    if "card_number" not in collection_columns:
        c.execute("ALTER TABLE collection ADD COLUMN card_number INTEGER DEFAULT 0")
        print("✅ Добавлена колонка card_number в collection")
    
    if "duplicates" not in collection_columns:
        c.execute("ALTER TABLE collection ADD COLUMN duplicates INTEGER DEFAULT 1")
        print("✅ Добавлена колонка duplicates в collection")
    
    c.execute("PRAGMA table_info(friends)")
    friends_columns = [col[1] for col in c.fetchall()]
    
    if not friends_columns:
        c.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                user_id INTEGER,
                friend_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, friend_id),
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(friend_id) REFERENCES users(user_id)
            )
        ''')
        print("✅ Создана таблица friends")
    
    conn.commit()
    conn.close()
    print("✅ Миграция БД завершена")

def get_user(user_id: int) -> Dict[str, Any]:
    conn = get_connection()
    c = conn.cursor()
    
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
    if not kwargs:
        return
    
    def _update():
        conn = get_connection()
        c = conn.cursor()
        fields = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]
        c.execute(f"UPDATE users SET {fields} WHERE user_id = ?", values)
        conn.commit()
        conn.close()
    
    with_retry(_update)

def get_collection(user_id: int) -> Dict[str, Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT hero_key, hero_data, card_number, duplicates FROM collection WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    result = {}
    for key, data, number, duplicates in rows:
        hero = json.loads(data)
        hero['card_number'] = number or 0
        hero['duplicates'] = duplicates or 1
        result[key] = hero
    conn.close()
    return result

def get_collection_with_duplicates(user_id: int) -> List[Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT hero_key, hero_data, card_number, duplicates FROM collection WHERE user_id = ? ORDER BY card_number", (user_id,))
    rows = c.fetchall()
    result = []
    for key, data, number, duplicates in rows:
        hero = json.loads(data)
        hero['card_number'] = number or 0
        hero['duplicates'] = duplicates or 1
        hero['hero_key'] = key
        result.append(hero)
    conn.close()
    return result

def add_hero_to_collection(user_id: int, hero: Dict) -> None:
    hero_key = f"{hero['author']} – {hero['name']}"
    hero_number = hero.get('card_number', 0)
    
    def _add():
        conn = get_connection()
        c = conn.cursor()
        
        c.execute(
            "SELECT id, duplicates FROM collection WHERE user_id = ? AND hero_key = ?",
            (user_id, hero_key)
        )
        row = c.fetchone()
        
        if row:
            card_id = row[0]
            new_duplicates = row[1] + 1
            c.execute(
                "UPDATE collection SET duplicates = ?, obtained_at = CURRENT_TIMESTAMP WHERE id = ?",
                (new_duplicates, card_id)
            )
            print(f"🔄 Дубликат: {hero_key} теперь {new_duplicates} шт.")
        else:
            c.execute(
                "INSERT INTO collection (user_id, hero_key, hero_data, card_number, duplicates) VALUES (?, ?, ?, ?, 1)",
                (user_id, hero_key, json.dumps(hero, ensure_ascii=False), hero_number)
            )
            print(f"✅ Новая карта: {hero_key}")
        
        conn.commit()
        conn.close()
    
    with_retry(_add)

def add_coins(user_id: int, amount: int) -> None:
    def _add_coins():
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET coins = coins + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
    
    with_retry(_add_coins)

def spend_coins(user_id: int, amount: int) -> bool:
    def _spend():
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
    
    return with_retry(_spend)

def get_card_by_number(user_id: int, number: int) -> Optional[Dict]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT hero_data, hero_key, card_number, duplicates 
        FROM collection 
        WHERE user_id = ? AND card_number = ?
    """, (user_id, number))
    row = c.fetchone()
    conn.close()
    if row:
        hero = json.loads(row[0])
        hero['card_number'] = row[2] or 0
        hero['hero_key'] = row[1]
        hero['duplicates'] = row[3] or 1
        return hero
    return None

def get_duplicates_count(user_id: int, hero_key: str) -> int:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT duplicates FROM collection WHERE user_id = ? AND hero_key = ?", (user_id, hero_key))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

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
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    rows = c.fetchall()
    conn.close()
    return [{"user_id": row[0]} for row in rows]

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
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

def get_leaderboard(limit: int = 10) -> list:
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
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM collection WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_heroes_by_rarity(user_id: int) -> Dict[str, int]:
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
    user = get_user(user_id)
    return {
        "streak": user.get("daily_quiz_streak", 0),
        "last_date": user.get("daily_quiz_last_date"),
        "done": user.get("daily_quiz_done", 0) == 1,
    }

def reset_daily_quiz(user_id: int) -> None:
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
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM collection WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    c.execute("DELETE FROM friends WHERE user_id = ? OR friend_id = ?", (user_id, user_id))
    conn.commit()
    conn.close()

# ==================== ФУНКЦИИ ДЛЯ ДРУЗЕЙ ====================

def add_friend(user_id: int, friend_id: int) -> bool:
    if user_id == friend_id:
        return False
    
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)",
            (user_id, friend_id)
        )
        c.execute(
            "INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)",
            (friend_id, user_id)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def remove_friend(user_id: int, friend_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "DELETE FROM friends WHERE user_id = ? AND friend_id = ?",
            (user_id, friend_id)
        )
        c.execute(
            "DELETE FROM friends WHERE user_id = ? AND friend_id = ?",
            (friend_id, user_id)
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_friends(user_id: int) -> list:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT friend_id FROM friends WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def is_friend(user_id: int, friend_id: int) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM friends WHERE user_id = ? AND friend_id = ?",
        (user_id, friend_id)
    )
    result = c.fetchone() is not None
    conn.close()
    return result