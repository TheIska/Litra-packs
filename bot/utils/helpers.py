import random
import re

def shuffle_question(question):
    """Возвращает вопрос без перемешивания вариантов"""
    return {
        "text": question["text"],
        "options": question["options"],
        "correct": question["correct"],
        "hero": question.get("hero", ""),
        "work": question.get("work", extract_work(question.get("text", ""))),
    }


def extract_work(question_text):
    """Извлекает название произведения из текста вопроса в скобках"""
    match = re.search(r'\(([^)]+)\)', question_text)
    return match.group(1) if match else ""