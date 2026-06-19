import os
import asyncio
from pathlib import Path
import requests
import urllib3
from dotenv import load_dotenv

# Отключаем SSL-предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Загружаем .env из корня проекта
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

print(f"Client ID: {GIGACHAT_CLIENT_ID[:15] if GIGACHAT_CLIENT_ID else 'НЕ НАЙДЕН'}...")
print(f"Scope: {GIGACHAT_SCOPE}")


def get_access_token():
    """Получает access_token от GigaChat"""
    if not GIGACHAT_CLIENT_ID or not GIGACHAT_CLIENT_SECRET:
        print("❌ GigaChat ключи не найдены")
        return None
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": "00000000-0000-0000-0000-000000000000"
    }
    data = {
        "client_id": GIGACHAT_CLIENT_ID,
        "client_secret": GIGACHAT_CLIENT_SECRET,
        "scope": GIGACHAT_SCOPE,
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Токен GigaChat получен")
            return token
        else:
            print(f"❌ Ошибка получения токена: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


def ask_gigachat(prompt: str) -> str:
    """Отправляет запрос к GigaChat"""
    token = get_access_token()
    if not token:
        return None
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": "Ты — эксперт по литературе. Отвечай кратко и понятно."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "Нет ответа")
        else:
            print(f"❌ Ошибка GigaChat: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None


async def get_explanation(question_text: str, correct_answer: str, options: list) -> str:
    """
    Генерирует краткое пояснение к вопросу через GigaChat.
    """
    question_clean = question_text.split(" (")[0] if " (" in question_text else question_text
    options_text = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])

    prompt = f"""Ты — эксперт по литературе. Дай краткое, понятное пояснение (2-3 предложения) к вопросу.

Вопрос: {question_clean}
Варианты ответов:
{options_text}
Правильный ответ: {correct_answer}

Напиши только пояснение, без лишних слов. Пояснение должно объяснять, почему этот ответ правильный. Используй эмодзи: 📚 ✍️ 🎭 📖."""

    # Запускаем в отдельном потоке, чтобы не блокировать асинхронный код
    result = await asyncio.to_thread(ask_gigachat, prompt)
    
    if result:
        return result
    else:
        return f"✅ Правильный ответ: {correct_answer}"