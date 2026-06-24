import os
import json
import requests
from typing import Optional
from datetime import datetime, timedelta

# Токены и настройки
GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

# Кеш токена
_token_cache = {
    "access_token": None,
    "expires_at": None
}


def get_access_token() -> Optional[str]:
    """Получает access token для GigaChat"""
    global _token_cache
    
    # Проверяем кеш
    if _token_cache["access_token"] and _token_cache["expires_at"] > datetime.now():
        return _token_cache["access_token"]
    
    # Если нет ключей - возвращаем None
    if not GIGACHAT_CLIENT_ID or not GIGACHAT_CLIENT_SECRET:
        print("⚠️ GigaChat API ключи не настроены")
        return None
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "12345678-1234-1234-1234-123456789012",
        "Authorization": f"Basic {GIGACHAT_CLIENT_ID}"
    }
    
    data = {
        "scope": GIGACHAT_SCOPE
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False)
        if response.status_code == 200:
            result = response.json()
            _token_cache["access_token"] = result.get("access_token")
            _token_cache["expires_at"] = datetime.now() + timedelta(seconds=result.get("expires_at", 1800))
            return _token_cache["access_token"]
        else:
            print(f"❌ Ошибка получения токена GigaChat: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка GigaChat auth: {e}")
        return None


def get_hero_description_gigachat_sync(hero_name: str, author: str, book: str) -> Optional[str]:
    """
    Генерирует описание литературного героя через GigaChat
    """
    try:
        token = get_access_token()
        if not token:
            return None
        
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        prompt = f"""
Ты эксперт по русской литературе. Напиши краткое, информативное описание литературного героя.

Герой: {hero_name}
Произведение: "{book}"
Автор: {author}

Требования:
- 2-3 предложения
- Без смайликов
- Без форматирования Markdown
- Интересно для школьников
- Упомяни ключевую характеристику героя
- Только текст, без лишних слов
"""
        
        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": "Ты эксперт по русской литературе. Отвечай кратко и по делу."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 150,
            "n": 1,
            "stream": False
        }
        
        response = requests.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("choices") and len(result["choices"]) > 0:
                description = result["choices"][0]["message"]["content"].strip()
                return description
            else:
                print(f"❌ GigaChat: нет ответа")
                return None
        else:
            print(f"❌ Ошибка GigaChat: {response.status_code}")
            return None
                    
    except Exception as e:
        print(f"❌ Ошибка GigaChat API: {e}")
        return None


async def get_hero_description_cached(hero_name: str, author: str, book: str) -> str:
    """
    Получает описание с кешированием в БД
    """
    from ..database import get_connection
    
    conn = get_connection()
    c = conn.cursor()
    
    # Создаем таблицу для кеша если нет
    c.execute('''
        CREATE TABLE IF NOT EXISTS hero_descriptions (
            hero_key TEXT PRIMARY KEY,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    
    hero_key = f"{author} – {hero_name}"
    
    # Ищем в кеше
    c.execute("SELECT description FROM hero_descriptions WHERE hero_key = ?", (hero_key,))
    row = c.fetchone()
    
    if row and row[0]:
        conn.close()
        return row[0]
    
    # Нет в кеше - генерируем через GigaChat
    description = get_hero_description_gigachat_sync(hero_name, author, book)
    
    # Если GigaChat не ответил - сохраняем сообщение об ошибке
    if not description:
        description = f"⚠️ Описание для {hero_name} временно недоступно. Попробуйте позже."
    
    # Сохраняем в кеш
    c.execute(
        "INSERT OR REPLACE INTO hero_descriptions (hero_key, description) VALUES (?, ?)",
        (hero_key, description)
    )
    conn.commit()
    
    conn.close()
    return description


async def generate_description_for_hero(hero: dict) -> str:
    """
    Удобная функция для получения описания героя
    """
    return await get_hero_description_cached(
        hero.get("name", ""),
        hero.get("author", ""),
        hero.get("book", "")
    )