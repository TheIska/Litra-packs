import os
import asyncio
from gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

print("🔄 Загрузка .env...")

GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

print(f"Client ID: {GIGACHAT_CLIENT_ID[:15] if GIGACHAT_CLIENT_ID else 'НЕ НАЙДЕН'}...")
print(f"Scope: {GIGACHAT_SCOPE}")

# Инициализация GigaChat
if GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET:
    try:
        giga = GigaChat(
            client_id=GIGACHAT_CLIENT_ID,
            client_secret=GIGACHAT_CLIENT_SECRET,
            scope=GIGACHAT_SCOPE,
        )
        print("✅ GigaChat инициализирован успешно!")
    except Exception as e:
        print(f"❌ Ошибка инициализации GigaChat: {e}")
        giga = None
else:
    print("❌ GigaChat API ключи не найдены в .env")
    giga = None


async def get_explanation(question_text: str, correct_answer: str, options: list) -> str:
    """
    Генерирует краткое пояснение к вопросу через GigaChat.
    """
    if not giga:
        print("⚠️ GigaChat не инициализирован, возвращаю только правильный ответ")
        return f"✅ Правильный ответ: {correct_answer}"

    question_clean = question_text.split(" (")[0] if " (" in question_text else question_text
    options_text = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])

    prompt = f"""Ты — эксперт по литературе. Дай краткое, понятное пояснение (2-3 предложения) к вопросу.

Вопрос: {question_clean}
Варианты ответов:
{options_text}
Правильный ответ: {correct_answer}

Напиши только пояснение, без лишних слов. Пояснение должно объяснять, почему этот ответ правильный. Используй эмодзи: 📚 ✍️ 🎭 📖."""

    try:
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты — эксперт по литературе. Отвечай кратко и понятно."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        print("📤 Отправляю запрос в GigaChat...")
        response = giga.chat(payload)
        result = response.choices[0].message.content.strip()
        print(f"📥 Получен ответ: {result[:50]}...")
        return result
    except Exception as e:
        print(f"❌ Ошибка GigaChat: {e}")
        return f"✅ Правильный ответ: {correct_answer}"