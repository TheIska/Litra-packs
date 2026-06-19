import os
import asyncio
from pathlib import Path
from pollinations import Pollinations
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

print("🔄 Инициализация Pollinations AI (бесплатно, без ключей)...")

# Создаём клиент (API-ключ не требуется!)
client = Pollinations()

print("✅ Pollinations AI готов к работе!")


async def get_explanation(question_text: str, correct_answer: str, options: list) -> str:
    """
    Генерирует краткое пояснение к вопросу через Pollinations AI.
    """
    question_clean = question_text.split(" (")[0] if " (" in question_text else question_text
    options_text = "\n".join([f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)])

    prompt = f"""Ты — эксперт по литературе. Дай краткое, понятное пояснение (2-3 предложения) к вопросу.

Вопрос: {question_clean}
Варианты ответов:
{options_text}
Правильный ответ: {correct_answer}

Напиши только пояснение, без лишних слов. Пояснение должно объяснять, почему этот ответ правильный. Используй эмодзи: 📚 ✍️ 🎭 📖."""

    try:
        # Отправляем запрос к Pollinations AI (совместимо с OpenAI API)
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Ты — эксперт по литературе. Отвечай кратко и понятно."},
                {"role": "user", "content": prompt}
            ],
            model="openai",  # или "mistral", "llama"
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ Ошибка Pollinations AI: {e}")
        return f"✅ Правильный ответ: {correct_answer}"