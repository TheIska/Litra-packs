import random

def shuffle_question(question):
    """Возвращает вопрос без перемешивания вариантов"""
    return {
        "text": question["text"],
        "options": question["options"],
        "correct": question["correct"],
        "hero": question.get("hero", "")
    }