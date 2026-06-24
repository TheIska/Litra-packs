import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")

def test_gigachat():
    print("🔍 Тестируем GigaChat API...")
    
    if not GIGACHAT_CLIENT_ID or not GIGACHAT_CLIENT_SECRET:
        print("❌ GigaChat API ключи не найдены в .env")
        print("   Добавьте в .env:")
        print("   GIGACHAT_CLIENT_ID=ваш_client_id")
        print("   GIGACHAT_CLIENT_SECRET=ваш_client_secret")
        return False
    
    print("✅ Ключи найдены")
    print(f"   Client ID: {GIGACHAT_CLIENT_ID[:10]}...")
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    # Кодируем в Base64
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
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            token = result.get("access_token")
            print(f"✅ Токен получен: {token[:20]}...")
            
            return test_generate_description(token)
        else:
            print(f"❌ Ошибка получения токена: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_generate_description(token):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    prompt = """
Ты эксперт по русской литературе. Напиши краткое описание литературного героя.

Герой: Евгений Онегин
Произведение: "Евгений Онегин"
Автор: А.С. Пушкин

Требования:
- 2-3 предложения
- Без смайликов
- Без форматирования
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
                print(f"✅ Описание получено:\n\n📝 {description}\n")
                return True
            else:
                print("❌ Нет ответа от GigaChat")
                return False
        else:
            print(f"❌ Ошибка GigaChat: {response.status_code}")
            print(f"   Ответ: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("   Тест GigaChat API")
    print("=" * 50)
    
    result = test_gigachat()
    
    if result:
        print("\n🎉 GigaChat работает корректно!")
    else:
        print("\n❌ GigaChat НЕ работает. Проверьте:")
        print("   1. Правильность ключей в .env")
        print("   2. Доступ к интернету")
        print("   3. Активность API ключа")