# bot/utils/image_generator.py

import io
import os
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

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
            "Поверь мне — счастье только там, где любят нас, где верят нам!",
            "Из двух друзей всегда один раб другого.",
            "Герой не тот, кто победил, а тот, кто не сдался."
        ],
        "Н.В. Гоголь": [
            "Какой же русский не любит быстрой езды?",
            "Нет слова, которое было бы так замашисто, как метко сказанное русское слово.",
            "В каждом слове бездна пространства."
        ],
        "Ф.М. Достоевский": [
            "Человек есть тайна. Ее надо разгадывать всю жизнь.",
            "Если Бога нет, то всё позволено.",
            "Красота спасет мир."
        ],
        "И.С. Тургенев": [
            "Во дни сомнений, во дни тягостных раздумий о судьбах моей родины, — ты один мне поддержка, о русский язык!",
            "Любовь сильнее смерти и страха смерти.",
            "Счастье — как здоровье: когда его не замечаешь, значит, оно есть."
        ]
    }
    author_quotes = quotes.get(author, ["С любовью к литературе"])
    return random.choice(author_quotes)


def create_vintage_texture(width, height):
    """Создаёт текстуру старой бумаги"""
    img = Image.new('RGB', (width, height), (245, 240, 230))
    draw = ImageDraw.Draw(img)
    
    # Лёгкий градиент
    for i in range(height):
        ratio = i / height
        dark = int(20 * (1 - abs(ratio - 0.5) * 2))
        draw.line([(0, i), (width, i)], fill=(245 - dark, 240 - dark, 230 - dark))
    
    # Минимальная текстура
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            if random.random() < 0.015:
                noise = random.randint(-10, 10)
                r = max(0, min(255, pixels[x, y][0] + noise))
                g = max(0, min(255, pixels[x, y][1] + noise))
                b = max(0, min(255, pixels[x, y][2] + noise))
                pixels[x, y] = (r, g, b)
    
    return img


def draw_stars(draw, x, y, count, color):
    """Рисует звёздочки для редкости"""
    for i in range(count):
        star_x = x - (count - 1) * 14 + i * 28
        # Рисуем 5-конечную звезду
        for angle in range(0, 360, 72):
            rad = math.radians(angle)
            dx = int(8 * math.cos(rad))
            dy = int(8 * math.sin(rad))
            draw.point((star_x + dx, y + dy), fill=color)
        draw.point((star_x, y), fill=color)


def create_hero_card(hero):
    width, height = 500, 700
    rarity = hero.get("rarity", "обычный")
    is_legendary = (rarity == "легендарный")
    
    # Генерируем номер карты (от 1 до 225)
    card_number = random.randint(1, 225)

    # Цвета
    colors = {
        "легендарный": {
            "bg": (240, 232, 215),
            "border": (180, 130, 70),
            "accent": (200, 150, 70),
            "text": (60, 40, 25),
            "sub": (100, 75, 50)
        },
        "эпический": {
            "bg": (235, 228, 220),
            "border": (140, 105, 155),
            "accent": (160, 120, 170),
            "text": (55, 40, 65),
            "sub": (95, 75, 105)
        },
        "редкий": {
            "bg": (230, 230, 225),
            "border": (85, 130, 165),
            "accent": (95, 145, 175),
            "text": (40, 50, 65),
            "sub": (75, 95, 115)
        },
        "обычный": {
            "bg": (225, 222, 215),
            "border": (130, 120, 110),
            "accent": (155, 145, 135),
            "text": (55, 50, 45),
            "sub": (95, 85, 75)
        }
    }

    pal = colors.get(rarity, colors["обычный"])

    # Создаём фон
    img = create_vintage_texture(width, height)
    draw = ImageDraw.Draw(img)

    # Простая рамка
    p = 18
    draw.rectangle([(p, p), (width - p, height - p)], outline=pal["border"], width=2)

    # Номер карты (в правом верхнем углу)
    font_number = load_font(16, "bold")
    number_text = f"№ {card_number:03d}"
    draw.text((width - 35, 25), number_text, fill=pal["border"], font=font_number, anchor="rt")

    # Заголовок Litra Packs
    y = 30
    font_title = load_font(20, "italic")
    draw.text((width//2, y), "✦ Litra Packs ✦", fill=pal["accent"], font=font_title, anchor="mt")
    y += 20

    # Портрет
    portrait_y = y + 5
    portrait_size = 210
    
    if is_legendary:
        portrait = load_portrait(hero)
        if portrait:
            portrait = portrait.resize((portrait_size, portrait_size), Image.Resampling.LANCZOS)
            
            mask = Image.new('L', (portrait_size, portrait_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((2, 2, portrait_size - 2, portrait_size - 2), fill=255)
            portrait.putalpha(mask)
            
            x = (width - portrait_size) // 2
            img.paste(portrait, (x, portrait_y), portrait)
            
            # Рамка вокруг портрета
            draw.ellipse([(x - 4, portrait_y - 4), (x + portrait_size + 4, portrait_y + portrait_size + 4)], 
                         outline=pal["border"], width=2)
            
            y = portrait_y + portrait_size + 25
        else:
            y = portrait_y + 230
    else:
        y = portrait_y + 170

    # Имя героя
    name = hero.get("name", "Неизвестный герой")
    font_name = load_font(44, "bold")
    
    # Тень для чёткости
    draw.text((width//2 + 1, y + 1), name, fill=(0, 0, 0, 20), font=font_name, anchor="mt")
    draw.text((width//2, y), name, fill=pal["text"], font=font_name, anchor="mt")
    y += 48

    # Информация
    font_info = load_font(20, "regular")
    font_small = load_font(17, "italic")
    font_quote = load_font(17, "italic")
    
    if is_legendary and portrait:
        author = hero.get("author", "")
        years = get_years(author)
        draw.text((width//2, y), years, fill=pal["sub"], font=font_small, anchor="mt")
        y += 28
        
        quote = get_random_quote(author)
        # Разбиваем цитату на строки
        words = quote.split()
        lines = []
        current = ""
        for word in words:
            if len(current + " " + word) <= 30:
                current += " " + word if current else word
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        
        for line in lines[:3]:
            draw.text((width//2, y), f'«{line}»', fill=pal["sub"], font=font_quote, anchor="mt")
            y += 26
        
        y += 10
        draw.text((width//2, y), f"— {author} —", fill=pal["sub"], font=font_small, anchor="mt")
        y += 40
    else:
        book = hero.get("book", hero.get("work", "Неизвестное произведение"))
        if len(book) > 30:
            book = book[:27] + "..."
        draw.text((width//2, y), f'«{book}»', fill=pal["sub"], font=font_info, anchor="mt")
        y += 30
        
        author = hero.get("author", "Неизвестный автор")
        draw.text((width//2, y), f"— {author} —", fill=pal["sub"], font=font_small, anchor="mt")
        y += 35

    # Редкость со звёздами
    labels = {
        "легендарный": "ЛЕГЕНДАРНЫЙ",
        "эпический": "ЭПИЧЕСКИЙ",
        "редкий": "РЕДКИЙ",
        "обычный": "ОБЫЧНЫЙ"
    }
    rarity_text = labels.get(rarity, "ОБЫЧНЫЙ")
    font_rare = load_font(22, "bold")
    
    colors_rare = {
        "легендарный": (200, 160, 80),
        "эпический": (160, 120, 170),
        "редкий": (100, 150, 180),
        "обычный": (150, 140, 130)
    }
    color = colors_rare.get(rarity, (150, 140, 130))
    
    # Звёздочки для редкости
    stars_count = {"легендарный": 5, "эпический": 4, "редкий": 3, "обычный": 2}
    stars = stars_count.get(rarity, 2)
    
    # Рисуем звёздочки над текстом
    star_y = y - 5
    draw_stars(draw, width//2, star_y, stars, color)
    
    # Текст редкости (с тенью для чёткости)
    draw.text((width//2 + 1, y + 1), rarity_text, fill=(0, 0, 0, 15), font=font_rare, anchor="mt")
    draw.text((width//2, y), rarity_text, fill=color, font=font_rare, anchor="mt")
    y += 40

    # Футер
    footer_y = height - 25
    font_footer = load_font(14, "italic")
    draw.text((width//2, footer_y), "Из собрания литературных героев", 
             fill=(pal["sub"][0], pal["sub"][1], pal["sub"][2], 160), 
             font=font_footer, anchor="mt")
    
    # Повышаем чёткость
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.05)

    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=95, optimize=True)
    bio.seek(0)
    return bio