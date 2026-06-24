# bot/friends.py
from .database import get_connection, get_user_by_id

def add_friend(user_id: int, friend_id: int) -> bool:
    """Добавляет друга в список"""
    if user_id == friend_id:
        return False
    
    conn = get_connection()
    c = conn.cursor()
    try:
        # Создаём таблицу если её нет
        c.execute('''
            CREATE TABLE IF NOT EXISTS friends (
                user_id INTEGER,
                friend_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, friend_id)
            )
        ''')
        c.execute("INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)", (user_id, friend_id))
        c.execute("INSERT OR IGNORE INTO friends (user_id, friend_id) VALUES (?, ?)", (friend_id, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"❌ Ошибка при добавлении друга: {e}")
        return False
    finally:
        conn.close()


def remove_friend(user_id: int, friend_id: int) -> bool:
    """Удаляет друга из списка"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("DELETE FROM friends WHERE user_id = ? AND friend_id = ?", (user_id, friend_id))
        c.execute("DELETE FROM friends WHERE user_id = ? AND friend_id = ?", (friend_id, user_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def get_friends(user_id: int) -> list:
    """Возвращает список друзей пользователя"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT friend_id FROM friends WHERE user_id = ?", (user_id,))
        rows = c.fetchall()
        return [row[0] for row in rows]
    except:
        return []
    finally:
        conn.close()


def is_friend(user_id: int, friend_id: int) -> bool:
    """Проверяет, являются ли пользователи друзьями"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT 1 FROM friends WHERE user_id = ? AND friend_id = ?", (user_id, friend_id))
        return c.fetchone() is not None
    except:
        return False
    finally:
        conn.close()