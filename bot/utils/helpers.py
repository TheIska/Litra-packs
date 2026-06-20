import random

def shuffle_question(question):
    """Перемешивает варианты ответов и обновляет правильный индекс"""
    indexed_options = list(enumerate(question["options"]))
    random.shuffle(indexed_options)
    
    new_options = [item[1] for item in indexed_options]
    correct_value = question["options"][question["correct"]]
    new_correct = new_options.index(correct_value)
    
    return {
        "text": question["text"],
        "options": new_options,
        "correct": new_correct,
        "hero": question.get("hero", "")
    }