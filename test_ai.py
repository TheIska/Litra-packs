import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.utils.ai_helper import get_explanation

def test():
    print("🧪 Тестируем Agnes AI (синхронный)...")
    
    result = get_explanation(
        question_text="Кто убивает Ленского на дуэли? (Евгений Онегин)",
        correct_answer="Онегин",
        options=["Онегин", "Зарецкий", "Татьяна", "Ленский"]
    )
    
    print("📖 Пояснение:")
    print(result)

if __name__ == "__main__":
    test()