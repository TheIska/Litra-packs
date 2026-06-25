import os
import sys
import time
import sqlite3
import requests
import base64
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# Настройки GigaChat
GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
GIGACHAT_SCOPE = "GIGACHAT_API_PERS"

# Путь к БД
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'bot_data.db')

# Импортируем ВСЕХ героев из models/hero.py
sys.path.insert(0, os.path.dirname(__file__))
from bot.models.hero import HEROES

print(f"📊 Загружено героев: {len(HEROES)}")

# Кеш токена
_token_cache = {
    "access_token": None,
    "expires_at": None
}


def get_access_token():
    global _token_cache
    
    if _token_cache["access_token"] and _token_cache["expires_at"] > time.time():
        return _token_cache["access_token"]
    
    if not GIGACHAT_CLIENT_ID or not GIGACHAT_CLIENT_SECRET:
        print("❌ GigaChat API ключи не настроены")
        return None
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    auth_string = f"{GIGACHAT_CLIENT_ID}:{GIGACHAT_CLIENT_SECRET}"
    auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "12345678-1234-1234-1234-123456789012",
        "Authorization": f"Basic {auth_b64}"
    }
    
    data = {
        "scope": GIGACHAT_SCOPE
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        if response.status_code == 200:
            result = response.json()
            _token_cache["access_token"] = result.get("access_token")
            _token_cache["expires_at"] = time.time() + 1800
            return _token_cache["access_token"]
        else:
            print(f"❌ Ошибка получения токена: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def generate_description(hero_name, author, book):
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
Ты эксперт по русской литературе. Напиши краткое описание литературного героя.

Герой: {hero_name}
Произведение: "{book}"
Автор: {author}

Требования:
- 2-3 предложения
- Без смайликов
- Без форматирования
- Интересно для школьников
- Упомяни ключевую характеристику героя
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
        
        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("choices") and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"].strip()
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def save_description(hero_key, description):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS hero_descriptions (
                hero_key TEXT PRIMARY KEY,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute(
            "INSERT OR REPLACE INTO hero_descriptions (hero_key, description) VALUES (?, ?)",
            (hero_key, description)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False


def main():
    print("=" * 60)
    print("🚀 Генерация описаний для ВСЕХ героев через GigaChat")
    print("=" * 60)
    print(f"📊 Всего героев: {len(HEROES)}")
    print("⏳ Это займёт ~15-20 минут...")
    print("-" * 60)
    
    # Проверяем подключение
    if not get_access_token():
        print("❌ Не удалось получить токен GigaChat. Проверьте ключи.")
        return
    
    success = 0
    fail = 0
    skipped = 0
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    for i, hero in enumerate(HEROES, 1):
        name = hero.get("name", "Неизвестный")
        author = hero.get("author", "Неизвестный автор")
        book = hero.get("book", "Неизвестное произведение")
        hero_key = f"{author} – {name}"
        
        # Проверяем, есть ли уже описание в БД
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT description FROM hero_descriptions WHERE hero_key = ?", (hero_key,))
        row = c.fetchone()
        conn.close()
        
        if row and row[0]:
            print(f"{i}/{len(HEROES)} ⏭️ {name} — уже есть")
            skipped += 1
            continue
        
        print(f"{i}/{len(HEROES)} 🔄 {name}...", end=" ")
        
        description = generate_description(name, author, book)
        
        if description:
            save_description(hero_key, description)
            success += 1
            print(f"✅ ({len(description)} символов)")
        else:
            fail += 1
            print("❌")
        
        # Пауза между запросами
        if i < len(HEROES):
            time.sleep(2)
    
    print("-" * 60)
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"   ✅ Сгенерировано: {success}")
    print(f"   ❌ Ошибок: {fail}")
    print(f"   ⏭️ Уже было: {skipped}")
    print("=" * 60)
    
    if fail > 0:
        print(f"\n⚠️ {fail} героев не получили описания.")
        print("📝 Их можно будет сгенерировать позже отдельно.")


if __name__ == "__main__":
    main()