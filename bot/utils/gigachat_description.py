import os
import json
import aiohttp
import asyncio
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


async def get_access_token() -> Optional[str]:
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
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data, ssl=False) as response:
                if response.status == 200:
                    result = await response.json()
                    _token_cache["access_token"] = result.get("access_token")
                    _token_cache["expires_at"] = datetime.now() + timedelta(seconds=result.get("expires_at", 1800))
                    return _token_cache["access_token"]
                else:
                    print(f"❌ Ошибка получения токена GigaChat: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ Ошибка GigaChat auth: {e}")
        return None


async def get_hero_description_gigachat(hero_name: str, author: str, book: str) -> Optional[str]:
    """
    Генерирует описание литературного героя через GigaChat
    """
    try:
        # Получаем токен
        token = await get_access_token()
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, ssl=False) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("choices") and len(result["choices"]) > 0:
                        description = result["choices"][0]["message"]["content"].strip()
                        return description
                    else:
                        print(f"❌ GigaChat: нет ответа")
                        return None
                else:
                    error_text = await response.text()
                    print(f"❌ Ошибка GigaChat: {response.status}")
                    return None
                    
    except Exception as e:
        print(f"❌ Ошибка GigaChat API: {e}")
        return None


# Функция-заглушка для получения описания (работает без GigaChat)
def get_fallback_description(hero_name: str, author: str, book: str) -> str:
    """Возвращает заглушку для описания, если GigaChat недоступен"""
    descriptions = {
        "Евгений Онегин": "Главный герой романа А.С. Пушкина. Молодой дворянин, разочарованный в светской жизни.",
        "Татьяна Ларина": "Идеал русской женщины в романе Пушкина. Чистая, искренняя, верная своим чувствам.",
        "Григорий Печорин": "Герой романа М.Ю. Лермонтова. Сложная личность, ищущая смысл жизни.",
        "Анна Каренина": "Героиня романа Л.Н. Толстого. Женщина, которая пожертвовала всем ради любви.",
        "Раскольников": "Герой романа Ф.М. Достоевского. Молодой человек, одержимый идеей сверхчеловека.",
        "Базаров": "Герой романа И.С. Тургенева. Нигилист, отрицающий все устои общества.",
        "Чичиков": "Герой поэмы Н.В. Гоголя. Предприимчивый авантюрист, скупающий мертвые души.",
    }
    
    # Ищем точное совпадение
    if hero_name in descriptions:
        return descriptions[hero_name]
    
    # Ищем частичное совпадение
    for key, value in descriptions.items():
        if key in hero_name or hero_name in key:
            return value
    
    # Если не нашли - возвращаем стандартное описание
    return f"{hero_name} — литературный герой произведения «{book}» автора {author}. Персонаж, который оставил след в истории русской литературы."


async def get_hero_description_cached(hero_name: str, author: str, book: str) -> str:
    """
    Получает описание с кешированием в БД
    """
    from ..database import get_connection
    
    # Проверяем кеш
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
    
    # Нет в кеше - пытаемся через GigaChat
    description = await get_hero_description_gigachat(hero_name, author, book)
    
    # Если GigaChat не ответил - используем заглушку
    if not description:
        description = get_fallback_description(hero_name, author, book)
    
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