# bot/utils/image_generator.py

import io
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

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
            "Гений и злодейство — две вещи несовместные.",
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
            "Нет слова, которое было бы так замашисто, как метко сказанное русское слово.",
            "В каждом слове бездна пространства.",
            "Чем кто умнее, тем он меньше понимает, что такое глупость."
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


def create_vintage_texture(width, height):
    """Создаёт реалистичную текстуру старой бумаги"""
    # Базовый цвет бумаги
    img = Image.new('RGB', (width, height), (245, 240, 230))
    draw = ImageDraw.Draw(img)
    
    # Лёгкий градиент (затемнение к краям)
    for i in range(height):
        ratio = i / height
        # Эффект выцветания к центру
        dark = int(30 * (1 - abs(ratio - 0.5) * 2))
        draw.line([(0, i), (width, i)], fill=(245 - dark, 240 - dark, 230 - dark))
    
    # Добавляем текстуру бумаги (шум)
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            if random.random() < 0.03:
                noise = random.randint(-15, 15)
                r = max(0, min(255, pixels[x, y][0] + noise))
                g = max(0, min(255, pixels[x, y][1] + noise))
                b = max(0, min(255, pixels[x, y][2] + noise))
                pixels[x, y] = (r, g, b)
    
    # Добавляем "пятна" как на старой бумаге
    for _ in range(random.randint(15, 30)):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(5, 30)
        color = (random.randint(210, 230), random.randint(200, 220), random.randint(180, 210))
        mask = Image.new('L', (radius * 2, radius * 2), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, radius * 2, radius * 2), fill=random.randint(50, 150))
        img.paste(color, (x - radius, y - radius), mask)
    
    return img


def draw_elegant_frame(draw, width, height, pal):
    """Рисует элегантную рамку в стиле XIX века"""
    # Отступы
    p = 25
    
    # Внешняя рамка (двойная)
    draw.rectangle([(p, p), (width - p, height - p)], outline=pal["border"], width=2)
    draw.rectangle([(p + 5, p + 5), (width - p - 5, height - p - 5)], outline=pal["border_light"], width=1)
    draw.rectangle([(p + 10, p + 10), (width - p - 10, height - p - 10)], outline=pal["border"], width=1)
    
    # Декоративные уголки (виньетки)
    corner_size = 35
    corners = [
        (p + 10, p + 10, 1, 1),      # левый верхний
        (width - p - 10, p + 10, -1, 1),  # правый верхний
        (p + 10, height - p - 10, 1, -1), # левый нижний
        (width - p - 10, height - p - 10, -1, -1) # правый нижний
    ]
    
    for cx, cy, dx, dy in corners:
        # Внешний орнамент
        for i in range(3, 0, -1):
            size = corner_size * i // 3
            draw.arc([cx - size, cy - size, cx + size, cy + size], 
                     0 if dx > 0 else 90, 
                     90 if dy > 0 else 180, 
                     fill=pal["border_light"], width=1)
        
        # Внутренний узор (завиток)
        for j in range(4):
            angle = j * 90
            ax = cx + int(12 * dx * (1 if j < 2 else -1))
            ay = cy + int(12 * dy * (1 if j % 2 == 0 else -1))
            draw.arc([ax - 8, ay - 8, ax + 8, ay + 8], 
                     angle, angle + 45, 
                     fill=pal["accent"], width=1)


def draw_ornament_line(draw, x1, y1, x2, y2, pal, style="accent"):
    """Рисует декоративную линию с узором"""
    color = pal.get(style, pal["accent"])
    
    # Основная линия
    draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
    
    # Декоративные точки
    step = 15
    for x in range(x1 + 10, x2 - 10, step):
        y = y1 + (y2 - y1) * (x - x1) // (x2 - x1)
        draw.ellipse([(x - 2, y - 2), (x + 2, y + 2)], fill=color)
    
    # Маленькие ромбики
    for x in range(x1 + 20, x2 - 20, step * 2):
        y = y1 + (y2 - y1) * (x - x1) // (x2 - x1)
        points = [(x, y - 3), (x + 3, y), (x, y + 3), (x - 3, y)]
        draw.polygon(points, outline=pal["border_light"], width=1)


def draw_hero_name(draw, x, y, name, pal):
    """Рисует имя героя в стиле старинной книги"""
    font_name = load_font(36, "bold")
    
    # Тень
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        draw.text((x + dx, y + dy), name, fill=(0, 0, 0, 50), font=font_name, anchor="mt")
    
    # Основной текст с градиентом
    draw.text((x, y), name, fill=pal["text"], font=font_name, anchor="mt")
    
    # Декоративная подчёркивающая линия
    try:
        bbox = draw.textbbox((0, 0), name, font=font_name)
        text_width = bbox[2] - bbox[0]
    except:
        text_width = draw.textlength(name, font=font_name)
    
    line_y = y + 15
    draw_ornament_line(draw, x - text_width//2 - 10, line_y, x + text_width//2 + 10, line_y, pal)


def draw_quote_style(draw, x, y, quote, pal):
    """Рисует цитату в красивом оформлении"""
    font_quote = load_font(16, "italic")
    font_quote_small = load_font(14, "italic")
    
    # Разбиваем на строки
    words = quote.split()
    lines = []
    current_line = ""
    max_width = 300
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        try:
            test_width = draw.textlength(test_line, font=font_quote)
        except:
            test_width = len(test_line) * 12
        
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Большая кавычка
    big_font = load_font(40, "italic")
    draw.text((x, y - 5), "«", fill=pal["accent"], font=big_font, anchor="lt")
    
    # Текст
    line_height = font_quote.size + 6
    for i, line in enumerate(lines[:3]):
        text_y = y + i * line_height
        # Лёгкая тень
        draw.text((x + 18 + 1, text_y + 1), line, fill=(0, 0, 0, 30), font=font_quote)
        draw.text((x + 18, text_y), line, fill=pal["sub"], font=font_quote)
    
    # Закрывающая кавычка
    if lines:
        last_y = y + (len(lines[:3]) - 1) * line_height
        try:
            last_line_width = draw.textlength(lines[-1], font=font_quote)
        except:
            last_line_width = len(lines[-1]) * 12
        draw.text((x + 18 + last_line_width + 5, last_y - 5), "»", fill=pal["accent"], font=big_font, anchor="lt")


def draw_rarity_badge(draw, x, y, rarity, pal):
    """Рисует красивый значок редкости"""
    labels = {
        "легендарный": ("★ ЛЕГЕНДА★", (200, 160, 80)),
        "эпический": ("✦ ЭПИЧЕСКИЙ ✦", (160, 120, 170)),
        "редкий": ("♦ РЕДКИЙ ♦", (100, 150, 180)),
        "обычный": ("• ОБЫЧНЫЙ •", (150, 140, 130))
    }
    
    text, color = labels.get(rarity, ("ОБЫЧНЫЙ", (150, 140, 130)))
    font = load_font(14, "bold")
    
    # Ромбовидный фон
    size = 100
    points = [
        (x, y - 15),
        (x + size//2, y),
        (x, y + 15),
        (x - size//2, y)
    ]
    draw.polygon(points, outline=pal["border"], fill=(255, 255, 255, 180), width=1)
    
    # Текст
    draw.text((x, y), text, fill=color, font=font, anchor="mt")


def draw_vintage_ornament(draw, x, y, pal):
    """Рисует декоративный орнамент"""
    # Центральный узор
    for i in range(10, 0, -2):
        size = i * 3
        draw.arc([x - size, y - size//2, x + size, y + size//2], 
                180, 360, fill=pal["border_light"], width=1)
    
    # Маленькие звёздочки
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        import math
        rad = math.radians(angle)
        dx = int(20 * math.cos(rad))
        dy = int(10 * math.sin(rad))
        draw.point((x + dx, y + dy), fill=pal["accent"])


def create_hero_card(hero):
    width, height = 500, 700
    rarity = hero.get("rarity", "обычный")
    is_legendary = (rarity == "легендарный")

    # Улучшенные цветовые палитры
    colors = {
        "легендарный": {
            "bg": (240, 232, 215),
            "border": (180, 130, 70),
            "border_light": (200, 170, 120),
            "accent": (200, 150, 70),
            "text": (60, 40, 25),
            "sub": (100, 75, 50),
            "shadow": (80, 60, 40)
        },
        "эпический": {
            "bg": (235, 228, 220),
            "border": (140, 105, 155),
            "border_light": (175, 150, 185),
            "accent": (160, 120, 170),
            "text": (55, 40, 65),
            "sub": (95, 75, 105),
            "shadow": (70, 55, 80)
        },
        "редкий": {
            "bg": (230, 230, 225),
            "border": (85, 130, 165),
            "border_light": (140, 175, 200),
            "accent": (95, 145, 175),
            "text": (40, 50, 65),
            "sub": (75, 95, 115),
            "shadow": (50, 65, 80)
        },
        "обычный": {
            "bg": (225, 222, 215),
            "border": (130, 120, 110),
            "border_light": (175, 165, 155),
            "accent": (155, 145, 135),
            "text": (55, 50, 45),
            "sub": (95, 85, 75),
            "shadow": (70, 65, 60)
        }
    }

    pal = colors.get(rarity, colors["обычный"])

    # Создаём текстурированный фон
    img = create_vintage_texture(width, height)
    draw = ImageDraw.Draw(img)

    # Рамка
    draw_elegant_frame(draw, width, height, pal)

    # Верхний заголовок
    y = 45
    font_title = load_font(16, "italic")
    title_text = "✦ Литературный Герой ✦"
    draw.text((width//2, y), title_text, fill=pal["accent"], font=font_title, anchor="mt")
    y += 15
    
    # Декоративная линия
    draw_ornament_line(draw, 60, y, width - 60, y, pal)
    y += 30

    # Портрет
    portrait_y = y
    portrait_size = 170
    
    if is_legendary:
        portrait = load_portrait(hero)
        if portrait:
            portrait = portrait.resize((portrait_size, portrait_size), Image.Resampling.LANCZOS)
            
            # Создаём маску для круга с мягким краем
            mask = Image.new('L', (portrait_size, portrait_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            for i in range(portrait_size // 2):
                r = portrait_size // 2 - i
                mask_draw.ellipse((i, i, portrait_size - i, portrait_size - i), 
                                 fill=int(255 * (1 - i / (portrait_size // 2) * 0.3)))
            
            portrait.putalpha(mask)
            
            x = (width - portrait_size) // 2
            # Добавляем тень
            shadow = Image.new('RGBA', (portrait_size + 20, portrait_size + 20), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)
            shadow_draw.ellipse((10, 10, portrait_size + 10, portrait_size + 10), fill=(0, 0, 0, 50))
            img.paste(shadow, (x - 10, portrait_y - 10), shadow)
            
            img.paste(portrait, (x, portrait_y), portrait)
            
            # Элегантная рамка вокруг портрета
            draw.ellipse([(x - 8, portrait_y - 8), (x + portrait_size + 8, portrait_y + portrait_size + 8)], 
                         outline=pal["border"], width=2)
            draw.ellipse([(x - 4, portrait_y - 4), (x + portrait_size + 4, portrait_y + portrait_size + 4)], 
                         outline=pal["accent"], width=1)
            
            # Орнамент вокруг портрета
            for angle in range(0, 360, 45):
                import math
                rad = math.radians(angle)
                ox = x + portrait_size//2 + int((portrait_size//2 + 15) * math.cos(rad))
                oy = portrait_y + portrait_size//2 + int((portrait_size//2 + 15) * math.sin(rad))
                draw.ellipse([(ox - 3, oy - 3), (ox + 3, oy + 3)], fill=pal["accent"])
            
            y = portrait_y + portrait_size + 35
        else:
            y = portrait_y + 200
    else:
        y = portrait_y + 120

    # Имя героя
    name = hero.get("name", "Неизвестный герой")
    draw_hero_name(draw, width//2, y, name, pal)
    y += 35

    # Информация
    font_info = load_font(15, "regular")
    font_info_small = load_font(13, "italic")
    
    if is_legendary and portrait:
        # Годы жизни
        author = hero.get("author", "")
        years = get_years(author)
        draw.text((width//2, y), years, fill=pal["sub"], font=font_info_small, anchor="mt")
        y += 25
        
        # Цитата
        quote = get_random_quote(author)
        draw_quote_style(draw, 50, y, quote, pal)
        y += 100
        
        # Автор внизу
        draw.text((width//2, y), f"— {author} —", fill=pal["sub"], font=font_info_small, anchor="mt")
        y += 35
    else:
        # Произведение
        book = hero.get("book", hero.get("work", "Неизвестное произведение"))
        if len(book) > 30:
            book = book[:27] + "..."
        draw.text((width//2, y), f'«{book}»', fill=pal["sub"], font=font_info, anchor="mt")
        y += 25
        
        # Автор
        author = hero.get("author", "Неизвестный автор")
        draw.text((width//2, y), f"— {author} —", fill=pal["sub"], font=font_info_small, anchor="mt")
        y += 30

    # Декоративная линия перед редкостью
    draw_ornament_line(draw, 60, y, width - 60, y, pal)
    y += 25

    # Редкость
    draw_rarity_badge(draw, width//2, y, rarity, pal)
    y += 35

    # Футер
    footer_y = height - 25
    font_footer = load_font(11, "italic")
    draw.text((width//2, footer_y), "❧ Из собрания литературных героев ❧", 
             fill=(pal["sub"][0], pal["sub"][1], pal["sub"][2], 180), 
             font=font_footer, anchor="mt")
    
    # Добавляем небольшое винтажное размытие
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Улучшаем контраст для более "старинного" вида
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.1)
    
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(0.9)

    # Сохранение
    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=92, optimize=True)
    bio.seek(0)
    return bio