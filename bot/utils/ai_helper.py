import os
import asyncio
from gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

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
        return f"✅ Правильный ответ: {correct_answer}"

    # Очищаем вопрос от названия произведения в скобках
    question_clean = question_text.split(" (")[0] if " (" in question_text else question_text

    # Формируем варианты с буквами
    options_text = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])

    prompt = f"""Ты — эксперт по литературе. Дай краткое, понятное пояснение (2-3 предложения) к вопросу.

Вопрос: {question_clean}
Варианты ответов:
{options_text}
Правильный ответ: {correct_answer}

Напиши только пояснение, без лишних слов. Пояснение должно объяснять, почему этот ответ правильный. Используй эмодзи: 📚 ✍️ 🎭 📖."""

    try:
        def _sync_call():
            response = giga.chat(
                prompt,
                temperature=0.7,
                max_tokens=150,
            )
            return response.choices[0].message.content

        response = await asyncio.to_thread(_sync_call)
        return response.strip()
    except Exception as e:
        print(f"❌ Ошибка GigaChat: {e}")
        return f"✅ Правильный ответ: {correct_answer}"