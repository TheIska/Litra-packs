# bot/utils/image_generator.py

import io
import os
import random
import math
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
    img = Image.new('RGB', (width, height), (245, 240, 230))
    draw = ImageDraw.Draw(img)
    
    # Лёгкий градиент
    for i in range(height):
        ratio = i / height
        dark = int(25 * (1 - abs(ratio - 0.5) * 2))
        draw.line([(0, i), (width, i)], fill=(245 - dark, 240 - dark, 230 - dark))
    
    # Текстура бумаги
    pixels = img.load()
    for x in range(width):
        for y in range(height):
            if random.random() < 0.02:
                noise = random.randint(-12, 12)
                r = max(0, min(255, pixels[x, y][0] + noise))
                g = max(0, min(255, pixels[x, y][1] + noise))
                b = max(0, min(255, pixels[x, y][2] + noise))
                pixels[x, y] = (r, g, b)
    
    return img


def draw_elegant_frame(draw, width, height, pal):
    """Рисует элегантную рамку"""
    p = 20
    
    # Основная рамка
    draw.rectangle([(p, p), (width - p, height - p)], outline=pal["border"], width=2)
    draw.rectangle([(p + 8, p + 8), (width - p - 8, height - p - 8)], outline=pal["border_light"], width=1)


def draw_hero_name(draw, x, y, name, pal):
    """Рисует имя героя без лишних полосок"""
    font_name = load_font(34, "bold")
    
    # Тень
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        draw.text((x + dx, y + dy), name, fill=(0, 0, 0, 30), font=font_name, anchor="mt")
    
    # Основной текст
    draw.text((x, y), name, fill=pal["text"], font=font_name, anchor="mt")


def draw_quote_style(draw, x, y, quote, pal):
    """Рисует цитату"""
    font_quote = load_font(15, "italic")
    font_big = load_font(30, "italic")
    
    # Разбиваем на строки
    words = quote.split()
    lines = []
    current_line = ""
    max_width = 370
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        try:
            test_width = draw.textlength(test_line, font=font_quote)
        except:
            test_width = len(test_line) * 9
        
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Открывающая кавычка
    draw.text((x, y - 5), "«", fill=pal["accent"], font=font_big, anchor="lt")
    
    # Текст
    line_height = font_quote.size + 4
    max_lines = min(len(lines), 3)
    for i in range(max_lines):
        text_y = y + i * line_height
        draw.text((x + 22, text_y), lines[i], fill=pal["sub"], font=font_quote)
    
    # Закрывающая кавычка
    if lines:
        last_y = y + (max_lines - 1) * line_height
        try:
            last_width = draw.textlength(lines[max_lines-1], font=font_quote)
        except:
            last_width = len(lines[max_lines-1]) * 9
        draw.text((x + 22 + last_width + 5, last_y - 5), "»", fill=pal["accent"], font=font_big, anchor="lt")


def draw_rarity_badge(draw, x, y, rarity, pal):
    """Рисует значок редкости"""
    labels = {
        "легендарный": "ЛЕГЕНДАРНЫЙ",
        "эпический": "ЭПИЧЕСКИЙ",
        "редкий": "РЕДКИЙ",
        "обычный": "ОБЫЧНЫЙ"
    }
    
    colors = {
        "легендарный": (200, 160, 80),
        "эпический": (160, 120, 170),
        "редкий": (100, 150, 180),
        "обычный": (150, 140, 130)
    }
    
    text = labels.get(rarity, "ОБЫЧНЫЙ")
    color = colors.get(rarity, (150, 140, 130))
    font = load_font(16, "bold")
    
    # Просто текст с декоративными символами
    symbols = {
        "легендарный": "✦",
        "эпический": "✧",
        "редкий": "♦",
        "обычный": "•"
    }
    symbol = symbols.get(rarity, "•")
    
    draw.text((x, y), f"{symbol} {text} {symbol}", fill=color, font=font, anchor="mt")


def create_hero_card(hero):
    width, height = 500, 700
    rarity = hero.get("rarity", "обычный")
    is_legendary = (rarity == "легендарный")

    # Цветовые палитры
    colors = {
        "легендарный": {
            "bg": (240, 232, 215),
            "border": (180, 130, 70),
            "border_light": (200, 170, 120),
            "accent": (200, 150, 70),
            "text": (60, 40, 25),
            "sub": (100, 75, 50)
        },
        "эпический": {
            "bg": (235, 228, 220),
            "border": (140, 105, 155),
            "border_light": (175, 150, 185),
            "accent": (160, 120, 170),
            "text": (55, 40, 65),
            "sub": (95, 75, 105)
        },
        "редкий": {
            "bg": (230, 230, 225),
            "border": (85, 130, 165),
            "border_light": (140, 175, 200),
            "accent": (95, 145, 175),
            "text": (40, 50, 65),
            "sub": (75, 95, 115)
        },
        "обычный": {
            "bg": (225, 222, 215),
            "border": (130, 120, 110),
            "border_light": (175, 165, 155),
            "accent": (155, 145, 135),
            "text": (55, 50, 45),
            "sub": (95, 85, 75)
        }
    }

    pal = colors.get(rarity, colors["обычный"])

    # Создаём фон
    img = create_vintage_texture(width, height)
    draw = ImageDraw.Draw(img)

    # Рамка
    draw_elegant_frame(draw, width, height, pal)

    # Заголовок
    y = 38
    font_title = load_font(20, "italic")
    title_text = "✦ Litra Packs ✦"
    draw.text((width//2, y), title_text, fill=pal["accent"], font=font_title, anchor="mt")
    y += 28

    # Портрет
    portrait_y = y
    portrait_size = 180
    
    if is_legendary:
        portrait = load_portrait(hero)
        if portrait:
            portrait = portrait.resize((portrait_size, portrait_size), Image.Resampling.LANCZOS)
            
            # Маска для круга
            mask = Image.new('L', (portrait_size, portrait_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((2, 2, portrait_size - 2, portrait_size - 2), fill=255)
            
            portrait.putalpha(mask)
            
            x = (width - portrait_size) // 2
            img.paste(portrait, (x, portrait_y), portrait)
            
            # Рамка вокруг портрета
            draw.ellipse([(x - 6, portrait_y - 6), (x + portrait_size + 6, portrait_y + portrait_size + 6)], 
                         outline=pal["border"], width=2)
            draw.ellipse([(x - 3, portrait_y - 3), (x + portrait_size + 3, portrait_y + portrait_size + 3)], 
                         outline=pal["accent"], width=1)
            
            y = portrait_y + portrait_size + 25
        else:
            y = portrait_y + 190
    else:
        y = portrait_y + 120

    # Имя героя (без полоски)
    name = hero.get("name", "Неизвестный герой")
    draw_hero_name(draw, width//2, y, name, pal)
    y += 38

    # Информация
    font_info = load_font(15, "regular")
    font_info_small = load_font(13, "italic")
    
    if is_legendary and portrait:
        author = hero.get("author", "")
        years = get_years(author)
        draw.text((width//2, y), years, fill=pal["sub"], font=font_info_small, anchor="mt")
        y += 24
        
        quote = get_random_quote(author)
        draw_quote_style(draw, 40, y, quote, pal)
        y += 100
        
        draw.text((width//2, y), f"— {author} —", fill=pal["sub"], font=font_info_small, anchor="mt")
        y += 35
    else:
        book = hero.get("book", hero.get("work", "Неизвестное произведение"))
        if len(book) > 30:
            book = book[:27] + "..."
        draw.text((width//2, y), f'«{book}»', fill=pal["sub"], font=font_info, anchor="mt")
        y += 26
        
        author = hero.get("author", "Неизвестный автор")
        draw.text((width//2, y), f"— {author} —", fill=pal["sub"], font=font_info_small, anchor="mt")
        y += 30

    # Редкость (простой текст с символами)
    draw_rarity_badge(draw, width//2, y, rarity, pal)
    y += 30

    # Футер
    footer_y = height - 22
    font_footer = load_font(11, "italic")
    draw.text((width//2, footer_y), "❧ Из собрания литературных героев ❧", 
             fill=(pal["sub"][0], pal["sub"][1], pal["sub"][2], 180), 
             font=font_footer, anchor="mt")
    
    # Лёгкое размытие
    img = img.filter(ImageFilter.GaussianBlur(radius=0.3))
    
    # Повышаем чёткость
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.4)
    
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.05)

    # Сохранение
    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=95, optimize=True)
    bio.seek(0)
    return bio