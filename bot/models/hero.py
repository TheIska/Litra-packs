# bot/models/hero.py

# ============================================================
# ВСЕ ГЕРОИ С ФИКСИРОВАННЫМИ НОМЕРАМИ И ХАРАКТЕРИСТИКАМИ
# ============================================================

HEROES_BY_NUMBER = {
    # ==================== ЛЕГЕНДАРНЫЕ (5) - ВСЁ ПО 90 ====================
    1: {"name": "Александр Пушкин", "book": "Евгений Онегин", "author": "1799-1837", "rarity": "легендарный", "portrait": "pushkin.png", "card_number": 1, "strength": 90, "intelligence": 90, "kindness": 90},
    2: {"name": "Михаил Лермонтов", "book": "Герой нашего времени", "author": "1814-1841", "rarity": "легендарный", "portrait": "lermontov.png", "card_number": 2, "strength": 90, "intelligence": 90, "kindness": 90},
    3: {"name": "Николай Гоголь", "book": "Мёртвые души", "author": "1809-1852", "rarity": "легендарный", "portrait": "gogol.png", "card_number": 3, "strength": 90, "intelligence": 90, "kindness": 90},
    4: {"name": "Фёдор Достоевский", "book": "Преступление и наказание", "author": "1821-1881", "rarity": "легендарный", "portrait": "dostoevsky.png", "card_number": 4, "strength": 90, "intelligence": 90, "kindness": 90},
    5: {"name": "Иван Тургенев", "book": "Отцы и дети", "author": "1818-1883", "rarity": "легендарный", "portrait": "turgenev.png", "card_number": 5, "strength": 90, "intelligence": 90, "kindness": 90},

    # ==================== А.С. ПУШКИН ====================
    # --- Евгений Онегин ---
    6: {"name": "Евгений Онегин", "book": "Евгений Онегин", "author": "А.С. Пушкин", "rarity": "эпический", "card_number": 6, "strength": 72, "intelligence": 88, "kindness": 60},
    7: {"name": "Татьяна Ларина", "book": "Евгений Онегин", "author": "А.С. Пушкин", "rarity": "эпический", "card_number": 7, "strength": 60, "intelligence": 85, "kindness": 71},
    8: {"name": "Владимир Ленский", "book": "Евгений Онегин", "author": "А.С. Пушкин", "rarity": "редкий", "card_number": 8, "strength": 66, "intelligence": 82, "kindness": 60},
    9: {"name": "Ольга Ларина", "book": "Евгений Онегин", "author": "А.С. Пушкин", "rarity": "редкий", "card_number": 9, "strength": 60, "intelligence": 65, "kindness": 90},
    10: {"name": "Зарецкий", "book": "Евгений Онегин", "author": "А.С. Пушкин", "rarity": "обычный", "card_number": 10, "strength": 68, "intelligence": 62, "kindness": 45},
    11: {"name": "Няня Филипьевна", "book": "Евгений Онегин", "author": "А.С. Пушкин", "rarity": "обычный", "card_number": 11, "strength": 45, "intelligence": 70, "kindness": 92},
    12: {"name": "Трике", "book": "Евгений Онегин", "author": "А.С. Пушкин", "rarity": "обычный", "card_number": 12, "strength": 40, "intelligence": 55, "kindness": 60},
    13: {"name": "Гильо", "book": "Евгений Онегин", "author": "А.С. Пушкин", "rarity": "обычный", "card_number": 13, "strength": 55, "intelligence": 50, "kindness": 65},

    # --- Капитанская дочка ---
    14: {"name": "Пётр Гринёв", "book": "Капитанская дочка", "author": "А.С. Пушкин", "rarity": "эпический", "card_number": 14, "strength": 80, "intelligence": 85, "kindness": 70},
    15: {"name": "Емельян Пугачёв", "book": "Капитанская дочка", "author": "А.С. Пушкин", "rarity": "эпический", "card_number": 15, "strength": 92, "intelligence": 80, "kindness": 30},
    16: {"name": "Маша Миронова", "book": "Капитанская дочка", "author": "А.С. Пушкин", "rarity": "эпический", "card_number": 16, "strength": 70, "intelligence": 80, "kindness": 80},
    17: {"name": "Алексей Швабрин", "book": "Капитанская дочка", "author": "А.С. Пушкин", "rarity": "редкий", "card_number": 17, "strength": 83, "intelligence": 63, "kindness": 40},
    18: {"name": "Савельич", "book": "Капитанская дочка", "author": "А.С. Пушкин", "rarity": "редкий", "card_number": 18, "strength": 70, "intelligence": 65, "kindness": 92},
    19: {"name": "Иван Игнатьич", "book": "Капитанская дочка", "author": "А.С. Пушкин", "rarity": "редкий", "card_number": 19, "strength": 65, "intelligence": 58, "kindness": 75},
    20: {"name": "Василиса Егоровна", "book": "Капитанская дочка", "author": "А.С. Пушкин", "rarity": "редкий", "card_number": 20, "strength": 73, "intelligence": 80, "kindness": 78},
    21: {"name": "Зурин", "book": "Капитанская дочка", "author": "А.С. Пушкин", "rarity": "обычный", "card_number": 21, "strength": 72, "intelligence": 55, "kindness": 69},
    22: {"name": "Иван Кузьмич", "book": "Капитанская дочка", "author": "А.С. Пушкин", "rarity": "обычный", "card_number": 22, "strength": 87, "intelligence": 65, "kindness": 83},

    # ==================== М.Ю. ЛЕРМОНТОВ ====================
    # --- Герой нашего времени ---
    23: {"name": "Григорий Печорин", "book": "Герой нашего времени", "author": "М.Ю. Лермонтов", "rarity": "эпический", "card_number": 23, "strength": 88, "intelligence": 95, "kindness": 30},
    24: {"name": "Максим Максимыч", "book": "Герой нашего времени", "author": "М.Ю. Лермонтов", "rarity": "редкий", "card_number": 24, "strength": 80, "intelligence": 65, "kindness": 88},
    25: {"name": "Бэла", "book": "Герой нашего времени", "author": "М.Ю. Лермонтов", "rarity": "редкий", "card_number": 25, "strength": 60, "intelligence": 68, "kindness": 85},
    26: {"name": "Грушницкий", "book": "Герой нашего времени", "author": "М.Ю. Лермонтов", "rarity": "редкий", "card_number": 26, "strength": 8, "intelligence": 65, "kindness": 50},
    27: {"name": "Доктор Вернер", "book": "Герой нашего времени", "author": "М.Ю. Лермонтов", "rarity": "редкий", "card_number": 27, "strength": 55, "intelligence": 88, "kindness": 75},
    28: {"name": "Вулич", "book": "Герой нашего времени", "author": "М.Ю. Лермонтов", "rarity": "редкий", "card_number": 28, "strength": 82, "intelligence": 55, "kindness": 51},
    29: {"name": "Азамат", "book": "Герой нашего времени", "author": "М.Ю. Лермонтов", "rarity": "обычный", "card_number": 29, "strength": 65, "intelligence": 50, "kindness": 60},
    30: {"name": "Казбич", "book": "Герой нашего времени", "author": "М.Ю. Лермонтов", "rarity": "обычный", "card_number": 30, "strength": 78, "intelligence": 58, "kindness": 45},

    # --- Мцыри ---
    31: {"name": "Мцыри", "book": "Мцыри", "author": "М.Ю. Лермонтов", "rarity": "эпический", "card_number": 31, "strength": 82, "intelligence": 72, "kindness": 78},

    # ==================== Н.В. ГОГОЛЬ ====================
    # --- Ревизор ---
    32: {"name": "Иван Хлестаков", "book": "Ревизор", "author": "Н.В. Гоголь", "rarity": "эпический", "card_number": 32, "strength": 55, "intelligence": 70, "kindness": 40},
    33: {"name": "Антон Антонович Сквозник-Дмухановский", "book": "Ревизор", "author": "Н.В. Гоголь", "rarity": "редкий", "card_number": 33, "strength": 62, "intelligence": 84, "kindness": 50},
    34: {"name": "Марья Антоновна", "book": "Ревизор", "author": "Н.В. Гоголь", "rarity": "редкий", "card_number": 34, "strength": 48, "intelligence": 62, "kindness": 30},
    35: {"name": "Осип", "book": "Ревизор", "author": "Н.В. Гоголь", "rarity": "редкий", "card_number": 35, "strength": 65, "intelligence": 65, "kindness": 70},
    36: {"name": "Анна Андреевна", "book": "Ревизор", "author": "Н.В. Гоголь", "rarity": "обычный", "card_number": 36, "strength": 45, "intelligence": 60, "kindness": 60},
    37: {"name": "Земляника", "book": "Ревизор", "author": "Н.В. Гоголь", "rarity": "обычный", "card_number": 37, "strength": 50, "intelligence": 65, "kindness": 33},
    38: {"name": "Ляпкин-Тяпкин", "book": "Ревизор", "author": "Н.В. Гоголь", "rarity": "обычный", "card_number": 38, "strength": 48, "intelligence": 58, "kindness": 33},
    39: {"name": "Бобчинский", "book": "Ревизор", "author": "Н.В. Гоголь", "rarity": "обычный", "card_number": 39, "strength": 40, "intelligence": 53, "kindness": 60},
    40: {"name": "Добчинский", "book": "Ревизор", "author": "Н.В. Гоголь", "rarity": "обычный", "card_number": 40, "strength": 40, "intelligence": 53, "kindness": 60},

    # --- Мёртвые души ---
    41: {"name": "Павел Чичиков", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "эпический", "card_number": 41, "strength": 70, "intelligence": 90, "kindness": 45},
    42: {"name": "Манилов", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "редкий", "card_number": 42, "strength": 40, "intelligence": 80, "kindness": 85},
    43: {"name": "Коробочка", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "редкий", "card_number": 43, "strength": 66, "intelligence": 60, "kindness": 55},
    44: {"name": "Ноздрёв", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "редкий", "card_number": 44, "strength": 85, "intelligence": 45, "kindness": 35},
    45: {"name": "Собакевич", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "редкий", "card_number": 45, "strength": 81, "intelligence": 71, "kindness": 30},
    46: {"name": "Плюшкин", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "редкий", "card_number": 46, "strength": 60, "intelligence": 70, "kindness": 30},
    47: {"name": "Селифан", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "обычный", "card_number": 47, "strength": 65, "intelligence": 50, "kindness": 60},
    48: {"name": "Петрушка", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "обычный", "card_number": 48, "strength": 55, "intelligence": 48, "kindness": 55},
    49: {"name": "Капитан Копейкин", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "обычный", "card_number": 49, "strength": 40, "intelligence": 65, "kindness": 60},
    50: {"name": "Прокурор", "book": "Мёртвые души", "author": "Н.В. Гоголь", "rarity": "обычный", "card_number": 50, "strength": 55, "intelligence": 55, "kindness": 60},

    # ==================== А.С. ГРИБОЕДОВ ====================
    # --- Горе от ума ---
    51: {"name": "Александр Чацкий", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "эпический", "card_number": 51, "strength": 70, "intelligence": 89, "kindness": 79},
    52: {"name": "Павел Фамусов", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "эпический", "card_number": 52, "strength": 58, "intelligence": 87, "kindness": 55},
    53: {"name": "Софья Фамусова", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "редкий", "card_number": 53, "strength": 50, "intelligence": 82, "kindness": 76},
    54: {"name": "Алексей Молчалин", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "редкий", "card_number": 54, "strength": 50, "intelligence": 79, "kindness": 45},
    55: {"name": "Лизанька", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "редкий", "card_number": 55, "strength": 48, "intelligence": 72, "kindness": 80},
    56: {"name": "Сергей Скалозуб", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "редкий", "card_number": 56, "strength": 88, "intelligence": 40, "kindness": 45},
    57: {"name": "Репетилов", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "обычный", "card_number": 57, "strength": 52, "intelligence": 70, "kindness": 60},
    58: {"name": "Загорецкий", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "обычный", "card_number": 58, "strength": 48, "intelligence": 62, "kindness": 50},
    59: {"name": "Хлёстова", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "обычный", "card_number": 59, "strength": 45, "intelligence": 65, "kindness": 55},
    60: {"name": "Князь Тугоуховский", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "обычный", "card_number": 60, "strength": 50, "intelligence": 55, "kindness": 65},
    61: {"name": "Графиня Хрюмина", "book": "Горе от ума", "author": "А.С. Грибоедов", "rarity": "обычный", "card_number": 61, "strength": 42, "intelligence": 58, "kindness": 60},

    # ==================== И.А. ГОНЧАРОВ ====================
    # --- Обломов ---
    62: {"name": "Илья Обломов", "book": "Обломов", "author": "И.А. Гончаров", "rarity": "эпический", "card_number": 62, "strength": 30, "intelligence": 98, "kindness": 95},
    63: {"name": "Андрей Штольц", "book": "Обломов", "author": "И.А. Гончаров", "rarity": "редкий", "card_number": 63, "strength": 84, "intelligence": 84, "kindness": 80},
    64: {"name": "Ольга Ильинская", "book": "Обломов", "author": "И.А. Гончаров", "rarity": "редкий", "card_number": 64, "strength": 55, "intelligence": 88, "kindness": 82},
    65: {"name": "Захар", "book": "Обломов", "author": "И.А. Гончаров", "rarity": "редкий", "card_number": 65, "strength": 60, "intelligence": 55, "kindness": 78},
    66: {"name": "Агафья Пшеницына", "book": "Обломов", "author": "И.А. Гончаров", "rarity": "редкий", "card_number": 66, "strength": 50, "intelligence": 60, "kindness": 80},

    # ==================== И.С. ТУРГЕНЕВ ====================
    # --- Отцы и дети ---
    67: {"name": "Евгений Базаров", "book": "Отцы и дети", "author": "И.С. Тургенев", "rarity": "эпический", "card_number": 67, "strength": 79, "intelligence": 85, "kindness": 55},
    68: {"name": "Аркадий Кирсанов", "book": "Отцы и дети", "author": "И.С. Тургенев", "rarity": "редкий", "card_number": 68, "strength": 70, "intelligence": 78, "kindness": 84},
    69: {"name": "Николай Петрович Кирсанов", "book": "Отцы и дети", "author": "И.С. Тургенев", "rarity": "редкий", "card_number": 69, "strength": 55, "intelligence": 80, "kindness": 95},
    70: {"name": "Павел Петрович Кирсанов", "book": "Отцы и дети", "author": "И.С. Тургенев", "rarity": "редкий", "card_number": 70, "strength": 67, "intelligence": 80, "kindness": 55},
    71: {"name": "Анна Одинцова", "book": "Отцы и дети", "author": "И.С. Тургенев", "rarity": "редкий", "card_number": 71, "strength": 60, "intelligence": 88, "kindness": 70},
    72: {"name": "Фенечка", "book": "Отцы и дети", "author": "И.С. Тургенев", "rarity": "обычный", "card_number": 72, "strength": 48, "intelligence": 62, "kindness": 85},
    73: {"name": "Катя Локтева", "book": "Отцы и дети", "author": "И.С. Тургенев", "rarity": "обычный", "card_number": 73, "strength": 50, "intelligence": 68, "kindness": 82},
    74: {"name": "Ситников", "book": "Отцы и дети", "author": "И.С. Тургенев", "rarity": "обычный", "card_number": 74, "strength": 52, "intelligence": 58, "kindness": 55},
    75: {"name": "Кукшина", "book": "Отцы и дети", "author": "И.С. Тургенев", "rarity": "обычный", "card_number": 75, "strength": 48, "intelligence": 62, "kindness": 60},

    # ==================== Ф.М. ДОСТОЕВСКИЙ ====================
    # --- Преступление и наказание ---
    76: {"name": "Родион Раскольников", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "эпический", "card_number": 76, "strength": 80, "intelligence": 83, "kindness": 67},
    77: {"name": "Соня Мармеладова", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "эпический", "card_number": 77, "strength": 50, "intelligence": 72, "kindness": 99},
    78: {"name": "Порфирий Петрович", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "редкий", "card_number": 78, "strength": 67, "intelligence": 92, "kindness": 68},
    79: {"name": "Дмитрий Разумихин", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "редкий", "card_number": 79, "strength": 79, "intelligence": 79, "kindness": 85},
    80: {"name": "Аркадий Свидригайлов", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "редкий", "card_number": 80, "strength": 67, "intelligence": 83, "kindness": 30},
    81: {"name": "Семён Мармеладов", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "редкий", "card_number": 81, "strength": 40, "intelligence": 70, "kindness": 72},
    82: {"name": "Катерина Ивановна", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "редкий", "card_number": 82, "strength": 45, "intelligence": 69, "kindness": 70},
    83: {"name": "Авдотья Раскольникова", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "редкий", "card_number": 83, "strength": 58, "intelligence": 79, "kindness": 90},
    84: {"name": "Пётр Лужин", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "обычный", "card_number": 84, "strength": 60, "intelligence": 40, "kindness": 30},
    85: {"name": "Зосимов", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "обычный", "card_number": 85, "strength": 55, "intelligence": 71, "kindness": 77},
    86: {"name": "Настасья Петровна", "book": "Преступление и наказание", "author": "Ф.М. Достоевский", "rarity": "обычный", "card_number": 86, "strength": 50, "intelligence": 58, "kindness": 75},

    # ==================== Л.Н. ТОЛСТОЙ ====================
    # --- Война и мир ---
    87: {"name": "Пьер Безухов", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "эпический", "card_number": 87, "strength": 52, "intelligence": 94, "kindness": 92},
    88: {"name": "Андрей Болконский", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "эпический", "card_number": 88, "strength": 88, "intelligence": 88, "kindness": 69},
    89: {"name": "Наташа Ростова", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "эпический", "card_number": 89, "strength": 69, "intelligence": 73, "kindness": 77},
    90: {"name": "Фёдор Долохов", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "эпический", "card_number": 90, "strength": 89, "intelligence": 76, "kindness": 40},
    91: {"name": "Николай Ростов", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "редкий", "card_number": 91, "strength": 82, "intelligence": 70, "kindness": 80},
    92: {"name": "Марья Болконская", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "редкий", "card_number": 92, "strength": 50, "intelligence": 90, "kindness": 95},
    93: {"name": "Элен Курагина", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "редкий", "card_number": 93, "strength": 60, "intelligence": 59, "kindness": 40},
    94: {"name": "Анатоль Курагин", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "редкий", "card_number": 94, "strength": 80, "intelligence": 56, "kindness": 40},
    95: {"name": "Михаил Кутузов", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "редкий", "card_number": 95, "strength": 60, "intelligence": 92, "kindness": 84},
    96: {"name": "Василий Денисов", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 96, "strength": 78, "intelligence": 70, "kindness": 75},
    97: {"name": "Соня Ростова", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 97, "strength": 52, "intelligence": 68, "kindness": 88},
    98: {"name": "Вера Ростова", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 98, "strength": 48, "intelligence": 70, "kindness": 55},
    99: {"name": "Берг", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 99, "strength": 55, "intelligence": 65, "kindness": 50},
    100: {"name": "Платон Каратаев", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 100, "strength": 65, "intelligence": 75, "kindness": 90},
    101: {"name": "Тушин", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 101, "strength": 68, "intelligence": 62, "kindness": 78},
    102: {"name": "Тимохин", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 102, "strength": 72, "intelligence": 58, "kindness": 72},
    103: {"name": "Алпатыч", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 103, "strength": 58, "intelligence": 68, "kindness": 75},
    104: {"name": "Дрон", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 104, "strength": 62, "intelligence": 55, "kindness": 65},
    105: {"name": "Борис Друбецкой", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 105, "strength": 55, "intelligence": 78, "kindness": 51},
    106: {"name": "Жюли Карагина", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 106, "strength": 45, "intelligence": 65, "kindness": 60},
    107: {"name": "Князь Василий Курагин", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 107, "strength": 60, "intelligence": 80, "kindness": 48},
    108: {"name": "Ипполит Курагин", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 108, "strength": 50, "intelligence": 55, "kindness": 45},
    109: {"name": "Наполеон Бонапарт", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 109, "strength": 68, "intelligence": 95, "kindness": 11},
    110: {"name": "Александр I", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 110, "strength": 74, "intelligence": 83, "kindness": 65},
    111: {"name": "Сперанский", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 111, "strength": 50, "intelligence": 79, "kindness": 55},
    112: {"name": "Багратион", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 112, "strength": 72, "intelligence": 75, "kindness": 76},
    113: {"name": "Мюрат", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 113, "strength": 78, "intelligence": 65, "kindness": 55},
    114: {"name": "Даву", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 114, "strength": 72, "intelligence": 75, "kindness": 50},
    115: {"name": "Растопчин", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 115, "strength": 62, "intelligence": 72, "kindness": 55},
    116: {"name": "Ахросимова", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 116, "strength": 55, "intelligence": 70, "kindness": 78},
    117: {"name": "Граф Воронцов", "book": "Война и мир", "author": "Л.Н. Толстой", "rarity": "обычный", "card_number": 117, "strength": 58, "intelligence": 72, "kindness": 65},

    # ==================== А.Н. ОСТРОВСКИЙ ====================
    # --- Гроза ---
    118: {"name": "Катерина Кабанова", "book": "Гроза", "author": "А.Н. Островский", "rarity": "эпический", "card_number": 118, "strength": 55, "intelligence": 75, "kindness": 88},
    119: {"name": "Кабаниха", "book": "Гроза", "author": "А.Н. Островский", "rarity": "редкий", "card_number": 119, "strength": 77, "intelligence": 70, "kindness": 40},
    120: {"name": "Тихон Кабанов", "book": "Гроза", "author": "А.Н. Островский", "rarity": "редкий", "card_number": 120, "strength": 60, "intelligence": 55, "kindness": 65},
    121: {"name": "Борис Григорьевич", "book": "Гроза", "author": "А.Н. Островский", "rarity": "редкий", "card_number": 121, "strength": 62, "intelligence": 68, "kindness": 72},
    122: {"name": "Варвара Кабанова", "book": "Гроза", "author": "А.Н. Островский", "rarity": "редкий", "card_number": 122, "strength": 68, "intelligence": 65, "kindness": 69},
    123: {"name": "Кулигин", "book": "Гроза", "author": "А.Н. Островский", "rarity": "обычный", "card_number": 123, "strength": 50, "intelligence": 81, "kindness": 80},
    124: {"name": "Дикой", "book": "Гроза", "author": "А.Н. Островский", "rarity": "обычный", "card_number": 124, "strength": 80, "intelligence": 52, "kindness": 35},
    125: {"name": "Феклуша", "book": "Гроза", "author": "А.Н. Островский", "rarity": "обычный", "card_number": 125, "strength": 42, "intelligence": 69, "kindness": 70},

    # ==================== Д.И. ФОНВИЗИН ====================
    # --- Недоросль ---
    126: {"name": "Госпожа Простакова", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "эпический", "card_number": 126, "strength": 58, "intelligence": 65, "kindness": 45},
    127: {"name": "Митрофан Простаков", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "редкий", "card_number": 127, "strength": 50, "intelligence": 45, "kindness": 55},
    128: {"name": "Стародум", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "редкий", "card_number": 128, "strength": 60, "intelligence": 93, "kindness": 80},
    129: {"name": "Правдин", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "редкий", "card_number": 129, "strength": 60, "intelligence": 78, "kindness": 75},
    130: {"name": "Софья", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "редкий", "card_number": 130, "strength": 48, "intelligence": 79, "kindness": 83},
    131: {"name": "Скотинин", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "обычный", "card_number": 131, "strength": 72, "intelligence": 45, "kindness": 40},
    132: {"name": "Милон", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "обычный", "card_number": 132, "strength": 70, "intelligence": 71, "kindness": 78},
    133: {"name": "Еремеевна", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "обычный", "card_number": 133, "strength": 55, "intelligence": 50, "kindness": 82},
    134: {"name": "Кутейкин", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "обычный", "card_number": 134, "strength": 48, "intelligence": 55, "kindness": 60},
    135: {"name": "Цифиркин", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "обычный", "card_number": 135, "strength": 52, "intelligence": 58, "kindness": 70},
    136: {"name": "Вральман", "book": "Недоросль", "author": "Д.И. Фонвизин", "rarity": "обычный", "card_number": 136, "strength": 45, "intelligence": 50, "kindness": 55},

    # ==================== А.П. ЧЕХОВ ====================
    # --- Ионыч ---
    137: {"name": "Ионыч", "book": "Ионыч", "author": "А.П. Чехов", "rarity": "эпический", "card_number": 137, "strength": 55, "intelligence": 78, "kindness": 65},
    
    # --- Человек в футляре ---
    138: {"name": "Беликов", "book": "Человек в футляре", "author": "А.П. Чехов", "rarity": "редкий", "card_number": 138, "strength": 48, "intelligence": 72, "kindness": 50},
    
    # --- Вишнёвый сад ---
    139: {"name": "Любовь Раневская", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "редкий", "card_number": 139, "strength": 45, "intelligence": 75, "kindness": 85},
    140: {"name": "Ермолай Лопахин", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "редкий", "card_number": 140, "strength": 75, "intelligence": 78, "kindness": 65},
    141: {"name": "Леонид Гаев", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "редкий", "card_number": 141, "strength": 50, "intelligence": 65, "kindness": 72},
    142: {"name": "Пётр Трофимов", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "редкий", "card_number": 142, "strength": 48, "intelligence": 80, "kindness": 78},
    143: {"name": "Варя (Варвара Михайловна)", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "обычный", "card_number": 143, "strength": 52, "intelligence": 62, "kindness": 82},
    144: {"name": "Аня Раневская", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "обычный", "card_number": 144, "strength": 42, "intelligence": 68, "kindness": 85},
    145: {"name": "Фирс", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "обычный", "card_number": 145, "strength": 45, "intelligence": 58, "kindness": 90},
    146: {"name": "Дуняша", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "обычный", "card_number": 146, "strength": 40, "intelligence": 55, "kindness": 75},
    147: {"name": "Епиходов", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "обычный", "card_number": 147, "strength": 50, "intelligence": 52, "kindness": 60},
    148: {"name": "Яша", "book": "Вишнёвый сад", "author": "А.П. Чехов", "rarity": "обычный", "card_number": 148, "strength": 55, "intelligence": 60, "kindness": 45},
    
    # --- Студент ---
    149: {"name": "Иван Великопольский", "book": "Студент", "author": "А.П. Чехов", "rarity": "обычный", "card_number": 149, "strength": 50, "intelligence": 72, "kindness": 78},

    # ==================== М. ГОРЬКИЙ ====================
    # --- На дне ---
    150: {"name": "Лука", "book": "На дне", "author": "М. Горький", "rarity": "редкий", "card_number": 150, "strength": 55, "intelligence": 78, "kindness": 92},
    151: {"name": "Сатин", "book": "На дне", "author": "М. Горький", "rarity": "редкий", "card_number": 151, "strength": 65, "intelligence": 85, "kindness": 55},
    152: {"name": "Васька Пепел", "book": "На дне", "author": "М. Горький", "rarity": "редкий", "card_number": 152, "strength": 78, "intelligence": 65, "kindness": 60},
    153: {"name": "Клещ (Андрей Митрич)", "book": "На дне", "author": "М. Горький", "rarity": "обычный", "card_number": 153, "strength": 62, "intelligence": 55, "kindness": 58},
    154: {"name": "Анна", "book": "На дне", "author": "М. Горький", "rarity": "обычный", "card_number": 154, "strength": 35, "intelligence": 50, "kindness": 70},
    155: {"name": "Настя", "book": "На дне", "author": "М. Горький", "rarity": "обычный", "card_number": 155, "strength": 40, "intelligence": 55, "kindness": 72},
    156: {"name": "Актёр", "book": "На дне", "author": "М. Горький", "rarity": "обычный", "card_number": 156, "strength": 45, "intelligence": 60, "kindness": 65},
    157: {"name": "Бубнов", "book": "На дне", "author": "М. Горький", "rarity": "обычный", "card_number": 157, "strength": 60, "intelligence": 58, "kindness": 50},
    158: {"name": "Костылёв", "book": "На дне", "author": "М. Горький", "rarity": "обычный", "card_number": 158, "strength": 55, "intelligence": 62, "kindness": 40},
    159: {"name": "Василиса", "book": "На дне", "author": "М. Горький", "rarity": "обычный", "card_number": 159, "strength": 50, "intelligence": 60, "kindness": 45},
    160: {"name": "Барон", "book": "На дне", "author": "М. Горький", "rarity": "обычный", "card_number": 160, "strength": 48, "intelligence": 65, "kindness": 55},

    # ==================== М.А. ШОЛОХОВ ====================
    # --- Тихий Дон ---
    161: {"name": "Григорий Мелехов", "book": "Тихий Дон", "author": "М.А. Шолохов", "rarity": "эпический", "card_number": 161, "strength": 92, "intelligence": 78, "kindness": 70},
    162: {"name": "Аксинья Астахова", "book": "Тихий Дон", "author": "М.А. Шолохов", "rarity": "эпический", "card_number": 162, "strength": 72, "intelligence": 65, "kindness": 82},
    163: {"name": "Наталья Мелехова", "book": "Тихий Дон", "author": "М.А. Шолохов", "rarity": "редкий", "card_number": 163, "strength": 55, "intelligence": 62, "kindness": 80},
    164: {"name": "Пантелей Прокофьевич", "book": "Тихий Дон", "author": "М.А. Шолохов", "rarity": "редкий", "card_number": 164, "strength": 75, "intelligence": 60, "kindness": 65},
    165: {"name": "Ильинична", "book": "Тихий Дон", "author": "М.А. Шолохов", "rarity": "редкий", "card_number": 165, "strength": 50, "intelligence": 65, "kindness": 88},
    166: {"name": "Мишка Кошевой", "book": "Тихий Дон", "author": "М.А. Шолохов", "rarity": "редкий", "card_number": 166, "strength": 80, "intelligence": 60, "kindness": 50},
    167: {"name": "Дарья Мелехова", "book": "Тихий Дон", "author": "М.А. Шолохов", "rarity": "обычный", "card_number": 167, "strength": 55, "intelligence": 58, "kindness": 60},
    168: {"name": "Дуняшка Мелехова", "book": "Тихий Дон", "author": "М.А. Шолохов", "rarity": "обычный", "card_number": 168, "strength": 50, "intelligence": 62, "kindness": 75},
    169: {"name": "Степан Астахов", "book": "Тихий Дон", "author": "М.А. Шолохов", "rarity": "обычный", "card_number": 169, "strength": 78, "intelligence": 55, "kindness": 50},

    # ==================== Б.Л. ПАСТЕРНАК ====================
    # --- Доктор Живаго ---
    170: {"name": "Юрий Живаго", "book": "Доктор Живаго", "author": "Б.Л. Пастернак", "rarity": "эпический", "card_number": 170, "strength": 65, "intelligence": 92, "kindness": 85},
    171: {"name": "Лариса Антипова", "book": "Доктор Живаго", "author": "Б.Л. Пастернак", "rarity": "редкий", "card_number": 171, "strength": 55, "intelligence": 78, "kindness": 80},
    172: {"name": "Антонина Громова (Тоня)", "book": "Доктор Живаго", "author": "Б.Л. Пастернак", "rarity": "обычный", "card_number": 172, "strength": 50, "intelligence": 72, "kindness": 82},
    173: {"name": "Виктор Комаровский", "book": "Доктор Живаго", "author": "Б.Л. Пастернак", "rarity": "обычный", "card_number": 173, "strength": 62, "intelligence": 80, "kindness": 45},
    174: {"name": "Гордон", "book": "Доктор Живаго", "author": "Б.Л. Пастернак", "rarity": "обычный", "card_number": 174, "strength": 55, "intelligence": 72, "kindness": 65},
    175: {"name": "Ливерий Микулицын", "book": "Доктор Живаго", "author": "Б.Л. Пастернак", "rarity": "обычный", "card_number": 175, "strength": 68, "intelligence": 65, "kindness": 60},
    176: {"name": "Сима", "book": "Доктор Живаго", "author": "Б.Л. Пастернак", "rarity": "обычный", "card_number": 176, "strength": 48, "intelligence": 70, "kindness": 75},
    177: {"name": "Павел Антипов (Стрельников)", "book": "Доктор Живаго", "author": "Б.Л. Пастернак", "rarity": "обычный", "card_number": 177, "strength": 75, "intelligence": 72, "kindness": 55},

    # ==================== А.И. СОЛЖЕНИЦЫН ====================
    # --- Один день Ивана Денисовича ---
    178: {"name": "Иван Денисович Шухов", "book": "Один день Ивана Денисовича", "author": "А.И. Солженицын", "rarity": "эпический", "card_number": 178, "strength": 82, "intelligence": 72, "kindness": 78},
    179: {"name": "Тюрин (бригадир)", "book": "Один день Ивана Денисовича", "author": "А.И. Солженицын", "rarity": "обычный", "card_number": 179, "strength": 75, "intelligence": 62, "kindness": 65},
    180: {"name": "Цезарь Маркович", "book": "Один день Ивана Денисовича", "author": "А.И. Солженицын", "rarity": "обычный", "card_number": 180, "strength": 55, "intelligence": 78, "kindness": 55},
    181: {"name": "Фетюков", "book": "Один день Ивана Денисовича", "author": "А.И. Солженицын", "rarity": "обычный", "card_number": 181, "strength": 60, "intelligence": 55, "kindness": 50},
    182: {"name": "Алик", "book": "Один день Ивана Денисовича", "author": "А.И. Солженицын", "rarity": "обычный", "card_number": 182, "strength": 50, "intelligence": 65, "kindness": 70},

    # ==================== Н.А. НЕКРАСОВ ====================
    # --- Кому на Руси жить хорошо ---
    183: {"name": "Савелий", "book": "Кому на Руси жить хорошо", "author": "Н.А. Некрасов", "rarity": "эпический", "card_number": 183, "strength": 80, "intelligence": 65, "kindness": 78},
    184: {"name": "Гриша Добросклонов", "book": "Кому на Руси жить хорошо", "author": "Н.А. Некрасов", "rarity": "редкий", "card_number": 184, "strength": 60, "intelligence": 82, "kindness": 80},
    185: {"name": "Ермила Гирин", "book": "Кому на Руси жить хорошо", "author": "Н.А. Некрасов", "rarity": "обычный", "card_number": 185, "strength": 70, "intelligence": 72, "kindness": 70},
    186: {"name": "Матрёна Тимофеевна", "book": "Кому на Руси жить хорошо", "author": "Н.А. Некрасов", "rarity": "обычный", "card_number": 186, "strength": 83, "intelligence": 68, "kindness": 88},
    187: {"name": "Влас", "book": "Кому на Руси жить хорошо", "author": "Н.А. Некрасов", "rarity": "обычный", "card_number": 187, "strength": 65, "intelligence": 60, "kindness": 72},
    188: {"name": "Ипат", "book": "Кому на Руси жить хорошо", "author": "Н.А. Некрасов", "rarity": "обычный", "card_number": 188, "strength": 58, "intelligence": 55, "kindness": 68},

    # ==================== Н.А. ОСТРОВСКИЙ (Как закалялась сталь) ====================
    189: {"name": "Павел Корчагин", "book": "Как закалялась сталь", "author": "Н.А. Островский", "rarity": "редкий", "card_number": 189, "strength": 85, "intelligence": 78, "kindness": 75},
    190: {"name": "Тоня Туманова", "book": "Как закалялась сталь", "author": "Н.А. Островский", "rarity": "обычный", "card_number": 190, "strength": 48, "intelligence": 72, "kindness": 80},
    191: {"name": "Жухрай", "book": "Как закалялась сталь", "author": "Н.А. Островский", "rarity": "обычный", "card_number": 191, "strength": 75, "intelligence": 70, "kindness": 65},
    192: {"name": "Должников", "book": "Как закалялась сталь", "author": "Н.А. Островский", "rarity": "обычный", "card_number": 192, "strength": 62, "intelligence": 58, "kindness": 60},

    # ==================== А.А. БЛОК ====================
    # --- Двенадцать ---
    193: {"name": "Красноармеец Ванька", "book": "Двенадцать", "author": "А.А. Блок", "rarity": "обычный", "card_number": 193, "strength": 65, "intelligence": 50, "kindness": 55},
    194: {"name": "Красноармеец Петька", "book": "Двенадцать", "author": "А.А. Блок", "rarity": "обычный", "card_number": 194, "strength": 62, "intelligence": 48, "kindness": 58},
    195: {"name": "Катька", "book": "Двенадцать", "author": "А.А. Блок", "rarity": "обычный", "card_number": 195, "strength": 50, "intelligence": 55, "kindness": 65},
    196: {"name": "Старуха", "book": "Двенадцать", "author": "А.А. Блок", "rarity": "обычный", "card_number": 196, "strength": 35, "intelligence": 50, "kindness": 60},

    # ==================== В.В. МАЯКОВСКИЙ ====================
    197: {"name": "Лирический герой (поэт)", "book": "Облако в штанах", "author": "В.В. Маяковский", "rarity": "обычный", "card_number": 197, "strength": 55, "intelligence": 88, "kindness": 60},
    198: {"name": "Мария (возлюбленная)", "book": "Облако в штанах", "author": "В.В. Маяковский", "rarity": "обычный", "card_number": 198, "strength": 48, "intelligence": 72, "kindness": 80},

    # ==================== А.А. АХМАТОВА ====================
    199: {"name": "Лирическая героиня (мать)", "book": "Реквием", "author": "А.А. Ахматова", "rarity": "обычный", "card_number": 199, "strength": 45, "intelligence": 85, "kindness": 90},
    200: {"name": "Сын", "book": "Реквием", "author": "А.А. Ахматова", "rarity": "обычный", "card_number": 200, "strength": 50, "intelligence": 70, "kindness": 75},

    # ==================== А.А. ФАДЕЕВ ====================
    # --- Молодая гвардия ---
    201: {"name": "Олег Кошевой", "book": "Молодая гвардия", "author": "А.А. Фадеев", "rarity": "обычный", "card_number": 201, "strength": 72, "intelligence": 75, "kindness": 80},
    202: {"name": "Ульяна Громова", "book": "Молодая гвардия", "author": "А.А. Фадеев", "rarity": "обычный", "card_number": 202, "strength": 55, "intelligence": 72, "kindness": 85},
    203: {"name": "Любовь Шевцова", "book": "Молодая гвардия", "author": "А.А. Фадеев", "rarity": "обычный", "card_number": 203, "strength": 58, "intelligence": 70, "kindness": 82},
    204: {"name": "Сергей Тюленин", "book": "Молодая гвардия", "author": "А.А. Фадеев", "rarity": "обычный", "card_number": 204, "strength": 75, "intelligence": 65, "kindness": 78},
    205: {"name": "Иван Земнухов", "book": "Молодая гвардия", "author": "А.А. Фадеев", "rarity": "обычный", "card_number": 205, "strength": 68, "intelligence": 72, "kindness": 75},

    # ==================== ДРЕВНЕРУССКАЯ ЛИТЕРАТУРА ====================
    # --- Слово о полку Игореве ---
    206: {"name": "Князь Игорь", "book": "Слово о полку Игореве", "author": "древнерусская литература", "rarity": "редкий", "card_number": 206, "strength": 81, "intelligence": 75, "kindness": 67},
    207: {"name": "Ярославна", "book": "Слово о полку Игореве", "author": "древнерусская литература", "rarity": "обычный", "card_number": 207, "strength": 45, "intelligence": 78, "kindness": 90},
    208: {"name": "Всеволод", "book": "Слово о полку Игореве", "author": "древнерусская литература", "rarity": "обычный", "card_number": 208, "strength": 72, "intelligence": 69, "kindness": 70},
    209: {"name": "Святослав Киевский", "book": "Слово о полку Игореве", "author": "древнерусская литература", "rarity": "обычный", "card_number": 209, "strength": 70, "intelligence": 90, "kindness": 78},
    210: {"name": "Олег", "book": "Слово о полку Игореве", "author": "древнерусская литература", "rarity": "обычный", "card_number": 210, "strength": 68, "intelligence": 65, "kindness": 60},
    211: {"name": "Кончак", "book": "Слово о полку Игореве", "author": "древнерусская литература", "rarity": "обычный", "card_number": 211, "strength": 82, "intelligence": 60, "kindness": 50},
    212: {"name": "Гзак (Гза)", "book": "Слово о полку Игореве", "author": "древнерусская литература", "rarity": "обычный", "card_number": 212, "strength": 78, "intelligence": 55, "kindness": 48},
}

# Список всех героев
HEROES = list(HEROES_BY_NUMBER.values())

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def get_hero_by_number(number: int):
    return HEROES_BY_NUMBER.get(number)

def get_hero_by_name(name: str):
    for hero in HEROES:
        if hero["name"] == name:
            return hero
    return None

def get_heroes_by_author(author: str):
    return [h for h in HEROES if h["author"] == author]

def get_heroes_by_work(work: str):
    return [h for h in HEROES if h["book"] == work]

def get_authors():
    authors = set()
    for hero in HEROES:
        authors.add(hero["author"])
    return sorted(authors)

def get_works():
    works = set()
    for hero in HEROES:
        works.add(hero["book"])
    return sorted(works)

def get_total_heroes():
    return len(HEROES_BY_NUMBER)

def get_heroes_grouped():
    result = {}
    for hero in HEROES:
        author = hero["author"]
        work = hero["book"]
        if author not in result:
            result[author] = {}
        if work not in result[author]:
            result[author][work] = []
        result[author][work].append(hero)
    return result

def get_rarity_count():
    result = {"легендарный": 0, "эпический": 0, "редкий": 0, "обычный": 0}
    for hero in HEROES:
        rarity = hero.get("rarity", "обычный")
        if rarity in result:
            result[rarity] += 1
    return result

def get_all_heroes_sorted():
    """Возвращает всех героев, отсортированных по номеру"""
    return sorted(HEROES_BY_NUMBER.items())