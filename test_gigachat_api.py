import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")

print("=" * 60)
print("🧪 Тест GigaChat API")
print("=" * 60)

print(f"\n🔑 Client ID: {GIGACHAT_CLIENT_ID[:10] if GIGACHAT_CLIENT_ID else 'НЕ НАЙДЕН'}...")
print(f"🔑 Client Secret: {'✅ есть' if GIGACHAT_CLIENT_SECRET else '❌ нет'}")

if not GIGACHAT_CLIENT_ID or not GIGACHAT_CLIENT_SECRET:
    print("\n❌ Ошибка: ключи не найдены в .env")
    print("📝 Добавьте в .env:")
    print("   GIGACHAT_CLIENT_ID=ваш_client_id")
    print("   GIGACHAT_CLIENT_SECRET=ваш_client_secret")
    exit(1)

# 1. Получаем токен
print("\n🔄 Шаг 1: Получение токена...")

auth_string = f"{GIGACHAT_CLIENT_ID}:{GIGACHAT_CLIENT_SECRET}"
auth_b64 = base64.b64encode(auth_string.encode('ascii')).decode('ascii')

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "RqUID": "12345678-1234-1234-1234-123456789012",
    "Authorization": f"Basic {auth_b64}"
}

data = {
    "scope": "GIGACHAT_API_PERS"
}

try:
    response = requests.post(
        "https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        headers=headers,
        data=data,
        verify=False,
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"❌ Ошибка получения токена: {response.status_code}")
        print(f"   Ответ: {response.text[:200]}")
        exit(1)
    
    token_data = response.json()
    token = token_data.get("access_token")
    print(f"✅ Токен получен: {token[:20]}...")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    exit(1)

# 2. Генерируем описание
print("\n🔄 Шаг 2: Генерация описания героя...")

url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {token}"
}

prompt = """
Ты эксперт по русской литературе. Напиши краткое описание литературного героя.

Герой: Владимир Ленский
Произведение: "Евгений Онегин"
Автор: А.С. Пушкин

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

try:
    response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("choices") and len(result["choices"]) > 0:
            description = result["choices"][0]["message"]["content"].strip()
            print("\n📝 ОПИСАНИЕ ОТ GIGACHAT:")
            print("-" * 60)
            print(description)
            print("-" * 60)
            print("\n✅ GigaChat работает корректно!")
        else:
            print("❌ Нет ответа от GigaChat")
    else:
        print(f"❌ Ошибка GigaChat: {response.status_code}")
        print(f"   Ответ: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")