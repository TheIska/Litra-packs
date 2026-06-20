# bot/utils/image_generator.py

import io
import os
import random
from PIL import Image, ImageDraw, ImageFont

def load_font(size, style="regular"):
    """Загружает шрифт из папки static/fonts"""
    try:
        font_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')
        font_files = {"regular": "regular.ttf", "italic": "italic.ttf", "bold": "bold.ttf"}
        font_file = font_files.get(style, "regular.ttf")
        font_path = os.path.join(font_dir, font_file)
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        if os.path.exists(font_dir):
            for f in os.listdir(font_dir):
                if f.endswith('.ttf') or f.endswith('.otf'):
                    return ImageFont.truetype(os.path.join(font_dir, f), size)
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()


def load_portrait(hero):
    """Загружает портрет для легендарного героя"""
    if hero.get("rarity") != "легендарный":
        return None
    
    portrait_map = {
        "Александр Пушкин": "pushkin.png",
        "Михаил Лермонтов": "lermontov.png",
        "Николай Гоголь": "gogol.png",
        "Фёдор Достоевский": "dostoevsky.png",
        "Иван Тургенев": "turgenev.png",
    }
    
    filename = portrait_map.get(hero.get("name", ""))
    if not filename:
        return None
    
    portrait_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'portraits', filename)
    if os.path.exists(portrait_path):
        try:
            return Image.open(portrait_path).convert("RGBA")
        except:
            return None
    return None


def get_years(author):
    years = {
        "А.С. Пушкин": "1799–1837",
        "М.Ю. Лермонтов": "1814–1841",
        "Н.В. Гоголь": "1809–1852",
        "Ф.М. Достоевский": "1821–1881",
        "И.С. Тургенев": "1818–1883",
    }
    return years.get(author, "")


def get_random_quote(author):
    quotes = {
        "А.С. Пушкин": [
            "Я жить хочу, чтоб мыслить и страдать.",
            "Гений и злодейство — две вещи несовместимые.",
            "Привычка свыше нам дана, замена счастию она.",
            "Мой друг, отчизне посвятим души прекрасные порывы!"
        ],
        "М.Ю. Лермонтов": [
            "Гений, прикованный к чиновничьему столу, должен умереть или сойти с ума.",
            "Поверь мне — счастье только там, где любят нас, где верят нам!",
            "Из двух друзей всегда один раб другого.",
            "Герой не тот, кто победил, а тот, кто не сдался."
        ],
        "Н.В. Гоголь": [
            "Какой же русский не любит быстрой езды?",
            "Есть у русского человека враг — лень.",
            "Нет слова, которое было бы так замашисто, как метко сказанное русское слово.",
            "В каждом слове бездна пространства."
        ],
        "Ф.М. Достоевский": [
            "Человек есть тайна. Ее надо разгадывать всю жизнь.",
            "Если Бога нет, то всё позволено.",
            "Красота спасет мир.",
            "Безответная любовь не унижает человека, а возвышает его."
        ],
        "И.С. Тургенев": [
            "Во дни сомнений, во дни тягостных раздумий о судьбах моей родины, — ты один мне поддержка, о русский язык!",
            "Любовь сильнее смерти и страха смерти.",
            "Счастье — как здоровье: когда его не замечаешь, значит, оно есть.",
            "Добро по указу — не добро."
        ]
    }
    author_quotes = quotes.get(author, ["С любовью к литературе"])
    return random.choice(author_quotes)


def create_textured_background(width, height, pal):
    """Создаёт текстурированный фон под старую бумагу"""
    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)
    
    # Основной фон с лёгким градиентом
    for i in range(height):
        ratio = i / height
        r = int(pal["bg"][0] * (1 - ratio * 0.3) + pal["bg2"][0] * ratio * 0.3)
        g = int(pal["bg"][1] * (1 - ratio * 0.3) + pal["bg2"][1] * ratio * 0.3)
        b = int(pal["bg"][2] * (1 - ratio * 0.3) + pal["bg2"][2] * ratio * 0.3)
        draw.line([(0, i), (width, i)], fill=(r, g, b))
    
    # Текстура бумаги (мелкие точки)
    for _ in range(300):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        brightness = random.randint(180, 220)
        draw.point((x, y), fill=(brightness, brightness - 5, brightness - 10))
    
    # Лёгкие потёртости по краям
    for _ in range(50):
        x = random.randint(0, 30)
        y = random.randint(0, height - 1)
        for i in range(3):
            draw.point((x + i, y), fill=(pal["bg"][0] + 20, pal["bg"][1] + 15, pal["bg"][2] + 10))
        x = random.randint(width - 30, width - 1)
        for i in range(3):
            draw.point((x - i, y), fill=(pal["bg"][0] + 20, pal["bg"][1] + 15, pal["bg"][2] + 10))
    
    return img


def draw_vintage_frame(draw, width, height, pal):
    """Рисует винтажную рамку"""
    border = 10
    
    # Внешняя тонкая рамка
    draw.rectangle([(border, border), (width - border, height - border)], outline=pal["border"], width=1)
    
    # Основная рамка с двойной линией
    draw.rectangle([(border + 10, border + 10), (width - border - 10, height - border - 10)], outline=pal["border"], width=1)
    
    # Украшение углов (маленькие завитки)
    corners = [
        (border + 15, border + 15),
        (width - border - 15, border + 15),
        (border + 15, height - border - 15),
        (width - border - 15, height - border - 15)
    ]
    for x, y in corners:
        for i in range(4):
            # ИСПРАВЛЕНО: заменяем outline на fill
            draw.arc([x - i * 6, y - i * 6, x + i * 6, y + i * 6], 0, 90, fill=pal["border"], width=1)
            draw.arc([x - i * 6 - 2, y - i * 6 - 2, x + i * 6 + 2, y + i * 6 + 2], 0, 90, fill=pal["accent"], width=1)


def create_hero_card(hero):
    width, height = 450, 640
    rarity = hero.get("rarity", "обычный")
    is_legendary = (rarity == "легендарный")

    # Цветовая палитра в стиле старой бумаги
    colors = {
        "легендарный": {
            "bg": (235, 225, 210),
            "bg2": (215, 200, 180),
            "border": (180, 120, 50),
            "accent": (200, 150, 70),
            "text": (50, 35, 20),
            "rare": (200, 150, 70),
            "sub": (100, 80, 55),
            "name_bg": (215, 200, 180),
            "seal": (180, 120, 50),
        },
        "эпический": {
            "bg": (230, 225, 215),
            "bg2": (210, 200, 190),
            "border": (140, 100, 150),
            "accent": (160, 120, 170),
            "text": (50, 35, 20),
            "rare": (160, 120, 170),
            "sub": (100, 80, 55),
            "name_bg": (210, 200, 190),
            "seal": (140, 100, 150),
        },
        "редкий": {
            "bg": (225, 225, 220),
            "bg2": (205, 205, 200),
            "border": (80, 130, 160),
            "accent": (90, 150, 180),
            "text": (50, 35, 20),
            "rare": (90, 150, 180),
            "sub": (100, 80, 55),
            "name_bg": (205, 205, 200),
            "seal": (80, 130, 160),
        },
        "обычный": {
            "bg": (220, 218, 210),
            "bg2": (200, 195, 185),
            "border": (130, 120, 110),
            "accent": (150, 140, 130),
            "text": (50, 35, 20),
            "rare": (150, 140, 130),
            "sub": (100, 80, 55),
            "name_bg": (200, 195, 185),
            "seal": (130, 120, 110),
        }
    }

    pal = colors.get(rarity, colors["обычный"])

    # Создаём фон
    img = create_textured_background(width, height, pal)
    draw = ImageDraw.Draw(img)

    # Загрузка шрифтов
    font_title = load_font(20, "italic")
    font_name = load_font(38, "bold")
    font_rare = load_font(22, "bold")
    font_footer = load_font(14, "italic")
    font_quote = load_font(15, "italic")
    font_years = load_font(16, "italic")
    font_book = load_font(18, "regular")
    font_author = load_font(16, "italic")
    font_label = load_font(18, "bold")

    # Рамка
    draw_vintage_frame(draw, width, height, pal)

    # Верхняя декоративная полоса
    y = 35
    draw.line([(40, y), (width - 40, y)], fill=pal["accent"], width=1)
    y += 5
    
    # Заголовок с вензелем
    title_text = "✦ LITRA PACKS ✦"
    draw.text((width//2, 28), title_text, fill=pal["accent"], font=font_title, anchor="mt")
    
    y = 55
    draw.line([(40, y), (width - 40, y)], fill=pal["accent"], width=1)
    y += 25

    # Портрет в старинной рамке
    portrait = None
    portrait_y = 80
    portrait_size = 150
    
    if is_legendary:
        portrait = load_portrait(hero)
        if portrait:
            # Изменяем размер портрета
            portrait = portrait.resize((portrait_size, portrait_size), Image.Resampling.LANCZOS)
            
            # Создаём маску для круга
            mask = Image.new('L', (portrait_size, portrait_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, portrait_size, portrait_size), fill=255)
            
            # Применяем маску
            portrait.putalpha(mask)
            
            x = (width - portrait_size) // 2
            img.paste(portrait, (x, portrait_y), portrait)
            
            # Овальная рамка вокруг портрета
            draw.ellipse([(x - 6, portrait_y - 6), (x + portrait_size + 6, portrait_y + portrait_size + 6)], 
                         outline=pal["border"], width=3)
            draw.ellipse([(x - 3, portrait_y - 3), (x + portrait_size + 3, portrait_y + portrait_size + 3)], 
                         outline=pal["accent"], width=1)
            
            name_y = portrait_y + portrait_size + 30
        else:
            name_y = 280
    else:
        name_y = 280

    # Имя героя (на стилизованной ленте)
    name = hero.get("name", "Неизвестный герой")
    
    # Создаём ленту для имени
    name_text_width = len(name) * 22 + 40
    name_bg = Image.new('RGBA', (name_text_width, 50), (pal["name_bg"][0], pal["name_bg"][1], pal["name_bg"][2], 180))
    name_draw = ImageDraw.Draw(name_bg)
    name_draw.rectangle([(0, 0), (name_text_width, 50)], outline=pal["border"], width=1)
    
    # Сохраняем ленту на основное изображение
    x = (width - name_text_width) // 2
    img.paste(name_bg, (x, name_y - 10), name_bg)
    
    # Тень для имени
    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
        draw.text((width//2 + dx, name_y + dy), name, fill=(0, 0, 0), font=font_name, anchor="mt")
    draw.text((width//2, name_y), name, fill=pal["text"], font=font_name, anchor="mt")

    y = name_y + 50
    draw.line([(40, y), (width - 40, y)], fill=pal["accent"], width=1)
    y += 25

    # Информация о герое
    if is_legendary and portrait:
        author = hero.get("author", "")
        years = get_years(author)
        draw.text((width//2, y), years, fill=pal["sub"], font=font_years, anchor="mt")
        y += 28
        
        quote = get_random_quote(author)
        words = quote.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 32:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        # Кавычки в стиле XIX века
        if lines:
            draw.text((width//2 - 10, y), "«", fill=pal["sub"], font=font_quote, anchor="mt")
            for i, line in enumerate(lines[:3]):
                draw.text((width//2 + 5, y + i * 20), line, fill=pal["sub"], font=font_quote, anchor="lt")
            draw.text((width//2 - 10, y + min(len(lines), 3) * 20 - 5), "»", fill=pal["sub"], font=font_quote, anchor="mt")
        
        y += len(lines[:3]) * 20 + 30
    else:
        # Для нелегендарных — книга и автор
        book = hero.get("book", hero.get("work", "Неизвестное произведение"))
        if len(book) > 28:
            book = book[:25] + "..."
        draw.text((width//2, y), f'"{book}"', fill=pal["sub"], font=font_book, anchor="mt")
        y += 28
        author = hero.get("author", "Неизвестный автор")
        draw.text((width//2, y), f'— {author} —', fill=pal["sub"], font=font_author, anchor="mt")
        y += 35

    # Редкость с декоративным элементом
    rare_labels = {"легендарный": "ЛЕГЕНДАРНЫЙ", "эпический": "ЭПИЧЕСКИЙ", "редкий": "РЕДКИЙ", "обычный": "ОБЫЧНЫЙ"}
    rare_text = rare_labels.get(rarity, "ОБЫЧНЫЙ")
    
    # Декоративная печать под редкостью
    seal_x = width // 2 - 40
    seal_y = y - 5
    draw.ellipse([(seal_x, seal_y), (seal_x + 80, seal_y + 30)], outline=pal["seal"], width=1)
    draw.text((width//2, y + 5), rare_text, fill=pal["rare"], font=font_rare, anchor="mt")
    
    y += 45
    draw.line([(40, y), (width - 40, y)], fill=pal["accent"], width=1)
    
    # Футер
    footer_y = height - 20
    draw.text((width//2, footer_y), "С любовью к литературе", fill=(pal["sub"][0], pal["sub"][1], pal["sub"][2], 150), font=font_footer, anchor="mt")

    # Сохранение в JPEG
    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=92, optimize=True)
    bio.seek(0)
    return bio