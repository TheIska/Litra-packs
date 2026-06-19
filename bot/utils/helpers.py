import random

def shuffle_question(question):
    """
    Перемешивает варианты ответов и обновляет правильный индекс
    """
    # Создаём список пар (индекс, вариант)
    indexed_options = list(enumerate(question["options"]))
    # Перемешиваем
    random.shuffle(indexed_options)
    
    # Новые варианты в перемешанном порядке
    new_options = [item[1] for item in indexed_options]
    
    # Находим новый индекс правильного ответа
    correct_value = question["options"][question["correct"]]
    new_correct = new_options.index(correct_value)
    
    return {
        "text": question["text"],
        "options": new_options,
        "correct": new_correct,
        "hero": question.get("hero", "")
    }