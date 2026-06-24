import os
import json
import requests
import base64
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
    
    if _token_cache["access_token"] and _token_cache["expires_at"] > datetime.now():
        return _token_cache["access_token"]
    
    if not GIGACHAT_CLIENT_ID or not GIGACHAT_CLIENT_SECRET:
        print("⚠️ GigaChat API ключи не настроены")
        return None
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    # Кодируем Client ID и Secret в Base64
    auth_string = f"{GIGACHAT_CLIENT_ID}:{GIGACHAT_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "12345678-1234-1234-1234-123456789012",
        "Authorization": f"Basic {auth_b64}"  # <-- Используем Base64
    }
    
    data = {
        "scope": GIGACHAT_SCOPE
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        if response.status_code == 200:
            result = response.json()
            _token_cache["access_token"] = result.get("access_token")
            _token_cache["expires_at"] = datetime.now() + timedelta(seconds=result.get("expires_at", 1800))
            return _token_cache["access_token"]
        else:
            print(f"❌ Ошибка получения токена GigaChat: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Ошибка GigaChat auth: {e}")
        return None


def get_hero_description_gigachat_sync(hero_name: str, author: str, book: str) -> Optional[str]:
    """Генерирует описание через GigaChat"""
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
- Без форматирования
- Интересно для школьников
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
                description = result["choices"][0]["message"]["content"].strip()
                return description
            return None
        else:
            print(f"❌ Ошибка GigaChat: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")
            return None
                    
    except Exception as e:
        print(f"❌ Ошибка GigaChat API: {e}")
        return None


# БАЗОВЫЕ ОПИСАНИЯ для всех героев
def get_basic_description(hero_name: str, author: str, book: str) -> str:
    """Возвращает базовое описание для героя"""
    descriptions = {
        # Пушкин
        "Евгений Онегин": "Главный герой романа А.С. Пушкина. Молодой дворянин, разочарованный в светской жизни, ищущий смысл существования.",
        "Татьяна Ларина": "Идеал русской женщины в романе Пушкина. Чистая, искренняя, верная своим чувствам.",
        "Владимир Ленский": "Молодой поэт, романтик, друг Онегина. Верит в идеалы, погибает на дуэли.",
        "Ольга Ларина": "Младшая сестра Татьяны, ветреная и жизнерадостная.",
        "Германн": "Герой «Пиковой дамы», одержимый тайной трёх карт. Азартный и безумный.",
        "Лиза": "Героиня «Пиковой дамы», воспитанница старой графини. Жертва любви к Германну.",
        "Самсон Вырин": "Станционный смотритель из повести Пушкина. Символ маленького человека.",
        
        # Лермонтов
        "Григорий Печорин": "Герой романа М.Ю. Лермонтова. Сложная и противоречивая личность, ищущая смысл жизни.",
        "Бэла": "Черкешенка, которую похитил Печорин. Символ чистой красоты.",
        "Максим Максимыч": "Добрый штабс-капитан. Воплощение честности и душевной теплоты.",
        "Мцыри": "Герой поэмы Лермонтова, юноша, бежавший из монастыря. Символ свободы.",
        
        # Гоголь
        "Павел Чичиков": "Герой поэмы Н.В. Гоголя. Предприимчивый авантюрист, скупающий мёртвые души.",
        "Ноздрев": "Отчаянный враль и кутила. Любит приврать и проигрывает всё в карты.",
        "Собакевич": "Помещик, похожий на медведя. Расчётливый и жадный, но честный в делах.",
        "Манилов": "Помещик, живущий в мире грёз. Сентиментальный и неспособный к хозяйству.",
        "Коробочка": "Помещица, недалёкая, но хозяйственная. Боится продешевить.",
        "Тарас Бульба": "Запорожский казак. Суровый воин и патриот.",
        "Андрий Бульба": "Младший сын Тараса. Предаёт отца ради любви.",
        "Остап Бульба": "Старший сын Тараса. Настоящий воин. Мужественно принимает смерть.",
        "Хлестаков": "Герой «Ревизора», лже-ревизор. Символ пустоты и вранья.",
        
        # Тургенев
        "Евгений Базаров": "Герой романа И.С. Тургенева. Нигилист, отрицающий все устои. Умный и дерзкий.",
        "Аркадий Кирсанов": "Друг Базарова, молодой дворянин. В душе остаётся романтиком.",
        "Павел Кирсанов": "Дядя Аркадия, бывший светский лев. Гордый и аристократичный.",
        "Анна Одинцова": "Богатая вдова, в которую влюбляется Базаров. Умная, красивая, но холодная.",
        "Герасим": "Герой рассказа «Муму», немой дворник. Символ бесправия.",
        
        # Достоевский
        "Родион Раскольников": "Герой романа Ф.М. Достоевского. Одержимый идеей сверхчеловека. Проходит от преступления к покаянию.",
        "Соня Мармеладова": "Чистая душа, сохранившая веру и любовь. Спасает Раскольникова.",
        "Дуня Раскольникова": "Гордая и самоотверженная сестра Родиона.",
        "Свидригайлов": "Двойник Раскольникова, развратный и циничный. Кончает с собой.",
        "Порфирий Петрович": "Следователь, умный психолог. Предлагает путь к покаянию.",
        "Мармеладов": "Пьяница-чиновник, отец Сони. Мучается от слабости.",
        "Алёша Карамазов": "Духовный и чистый юноша. Воплощение добра и любви.",
        "Иван Карамазов": "Интеллектуал, сомневающийся в Боге. Мучится вопросом о добре и зле.",
        "Дмитрий Карамазов": "Старший брат, живущий чувствами. Страдает и находит очищение.",
        "Грушенька": "Красавица с сложной судьбой. В итоге раскаивается.",
        "Старец Зосима": "Духовный наставник Алёши. Учит любви и прощению.",
        
        # Гончаров
        "Илья Обломов": "Герой романа И.А. Гончарова. Ленивый помещик, символ «обломовщины».",
        "Андрей Штольц": "Друг Обломова, деятельный и энергичный. Антипод Обломова.",
        "Ольга Ильинская": "Девушка, в которую влюблён Обломов. Символ деятельной любви.",
    }
    
    if hero_name in descriptions:
        return descriptions[hero_name]
    
    for key, value in descriptions.items():
        if key in hero_name or hero_name in key:
            return value
    
    return f"{hero_name} — литературный герой произведения «{book}» автора {author}. Персонаж, оставивший след в русской литературе."


async def get_hero_description_cached(hero_name: str, author: str, book: str) -> str:
    """Получает описание с кешированием в БД"""
    from ..database import get_connection
    
    conn = get_connection()
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS hero_descriptions (
            hero_key TEXT PRIMARY KEY,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    
    hero_key = f"{author} – {hero_name}"
    
    c.execute("SELECT description FROM hero_descriptions WHERE hero_key = ?", (hero_key,))
    row = c.fetchone()
    
    if row and row[0]:
        conn.close()
        return row[0]
    
    description = get_hero_description_gigachat_sync(hero_name, author, book)
    
    if not description:
        description = get_basic_description(hero_name, author, book)
        print(f"ℹ️ Использовано базовое описание для {hero_name}")
    
    c.execute(
        "INSERT OR REPLACE INTO hero_descriptions (hero_key, description) VALUES (?, ?)",
        (hero_key, description)
    )
    conn.commit()
    
    conn.close()
    return description


async def generate_description_for_hero(hero: dict) -> str:
    """Удобная функция для получения описания героя"""
    return await get_hero_description_cached(
        hero.get("name", ""),
        hero.get("author", ""),
        hero.get("book", "")
    )