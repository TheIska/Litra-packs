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


def load_logo():
    """Загружает логотип бота"""
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'images', 'logo.png')
    if os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Уменьшаем логотип до разумного размера
            logo.thumbnail((60, 60), Image.Resampling.LANCZOS)
            return logo
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}")
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
    
    # Лёгкие пятна
    for _ in range(10):
        x = random.randint(20, width - 20)
        y = random.randint(20, height - 20)
        radius = random.randint(15, 50)
        color = (random.randint(210, 235), random.randint(200, 225), random.randint(185, 215))
        for i in range(radius):
            alpha = int(25 * (1 - i / radius))
            draw.ellipse([(x - i, y - i), (x + i, y + i)], 
                        fill=(color[0], color[1], color[2], alpha))
    
    return img


def draw_elegant_frame(draw, width, height, pal):
    """Рисует элегантную рамку"""
    p = 18
    
    draw.rectangle([(p, p), (width - p, height - p)], outline=pal["border"], width=2)
    draw.rectangle([(p + 5, p + 5), (width - p - 5, height - p - 5)], outline=pal["border_light"], width=1)
    draw.rectangle([(p + 10, p + 10), (width - p - 10, height - p - 10)], outline=pal["border"], width=1)
    
    # Уголки
    corner_size = 22
    corners = [
        (p + 10, p + 10, 1, 1),
        (width - p - 10, p + 10, -1, 1),
        (p + 10, height - p - 10, 1, -1),
        (width - p - 10, height - p - 10, -1, -1)
    ]
    
    for cx, cy, dx, dy in corners:
        for i in range(3):
            size = corner_size - i * 6
            if size > 5:
                draw.arc([cx - size, cy - size, cx + size, cy + size], 
                         0 if dx > 0 else 90, 
                         90 if dy > 0 else 180, 
                         fill=pal["border_light"], width=1)


def draw_ornament_pattern(draw, x, y, width, pal, count=5):
    """Рисует декоративный узор"""
    spacing = width // count
    for i in range(count):
        pos_x = x + i * spacing + spacing // 2
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            dx = int(4 * math.cos(rad))
            dy = int(4 * math.sin(rad))
            draw.point((pos_x + dx, y + dy), fill=pal["border_light"])
        draw.ellipse([(pos_x - 2, y - 2), (pos_x + 2, y + 2)], fill=pal["accent"])


def draw_hero_name(draw, x, y, name, pal):
    """Рисует имя героя"""
    font_name = load_font(32, "bold")
    
    # Тень
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        draw.text((x + dx, y + dy), name, fill=(0, 0, 0, 25), font=font_name, anchor="mt")
    
    draw.text((x, y), name, fill=pal["text"], font=font_name, anchor="mt")
    
    # Подчёркивание
    try:
        bbox = draw.textbbox((0, 0), name, font=font_name)
        text_width = bbox[2] - bbox[0]
    except:
        text_width = len(name) * 18
    
    line_y = y + 18
    draw.line([(x - text_width//2 - 20, line_y), (x + text_width//2 + 20, line_y)], 
              fill=pal["accent"], width=1)
    draw.ellipse([(x - text_width//2 - 24, line_y - 3), (x - text_width//2 - 18, line_y + 3)], 
                 fill=pal["accent"])
    draw.ellipse([(x + text_width//2 + 18, line_y - 3), (x + text_width//2 + 24, line_y + 3)], 
                 fill=pal["accent"])


def draw_quote_style(draw, x, y, quote, pal):
    """Рисует цитату"""
    font_quote = load_font(15, "italic")
    font_big = load_font(30, "italic")
    
    words = quote.split()
    lines = []
    current_line = ""
    max_width = 350
    
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
    
    # Вертикальная линия
    line_height_total = len(lines[:3]) * 20 + 10
    draw.line([(x, y), (x, y + line_height_total)], fill=pal["border_light"], width=1)
    draw.ellipse([(x - 3, y - 3), (x + 3, y + 3)], fill=pal["accent"])
    draw.ellipse([(x - 3, y + line_height_total - 3), (x + 3, y + line_height_total + 3)], 
                 fill=pal["border_light"])
    
    draw.text((x + 15, y - 5), "«", fill=pal["accent"], font=font_big, anchor="lt")
    
    line_height = font_quote.size + 4
    max_lines = min(len(lines), 3)
    for i in range(max_lines):
        text_y = y + i * line_height
        draw.text((x + 36, text_y + 1), lines[i], fill=(0, 0, 0, 15), font=font_quote)
        draw.text((x + 35, text_y), lines[i], fill=pal["sub"], font=font_quote)
    
    if lines:
        last_y = y + (max_lines - 1) * line_height
        try:
            last_width = draw.textlength(lines[max_lines-1], font=font_quote)
        except:
            last_width = len(lines[max_lines-1]) * 9
        draw.text((x + 35 + last_width + 5, last_y - 5), "»", fill=pal["accent"], font=font_big, anchor="lt")


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
    
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
    except:
        text_width = len(text) * 10
    
    padding = 20
    rect_x1 = x - text_width//2 - padding
    rect_y1 = y - 14
    rect_x2 = x + text_width//2 + padding
    rect_y2 = y + 14
    
    draw.rectangle([(rect_x1, rect_y1), (rect_x2, rect_y2)], 
                   fill=(255, 255, 255, 180), outline=pal["border"], width=1)
    draw.rectangle([(rect_x1 + 3, rect_y1 + 3), (rect_x2 - 3, rect_y2 - 3)], 
                   outline=pal["border_light"], width=1)
    
    symbols = {
        "легендарный": "✦",
        "эпический": "✧",
        "редкий": "♦",
        "обычный": "•"
    }
    symbol = symbols.get(rarity, "•")
    
    draw.text((x + 1, y + 1), f"{symbol} {text} {symbol}", fill=(0, 0, 0, 20), font=font, anchor="mt")
    draw.text((x, y), f"{symbol} {text} {symbol}", fill=color, font=font, anchor="mt")


def draw_book_illustration(draw, x, y, width, height, pal, book_title):
    """Рисует стилизованную обложку книги"""
    # Рамка книги
    draw.rectangle([(x, y), (x + width, y + height)], outline=pal["border"], width=2)
    draw.rectangle([(x + 5, y + 5), (x + width - 5, y + height - 5)], outline=pal["border_light"], width=1)
    
    # Корешок
    draw.line([(x + 15, y), (x + 15, y + height)], fill=pal["border"], width=1)
    draw.line([(x + 17, y), (x + 17, y + height)], fill=pal["border_light"], width=1)
    
    # Название на обложке
    font_book = load_font(16, "bold")
    # Разбиваем название на строки
    words = book_title.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) <= 15:
            current_line += " " + word if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Центрируем название
    text_y = y + height//2 - (len(lines) * 20)//2
    for line in lines[:3]:
        draw.text((x + width//2 + 10, text_y), line, fill=pal["text"], font=font_book, anchor="mt")
        text_y += 20
    
    # Декоративные элементы
    draw_ornament_pattern(draw, x + width//2 + 10, y + 15, 80, pal, 3)
    draw_ornament_pattern(draw, x + width//2 + 10, y + height - 15, 80, pal, 3)


def draw_logo(draw, x, y, pal, logo_img):
    """Рисует логотип бота"""
    if logo_img:
        # Вставляем загруженный логотип
        logo_x = x - logo_img.width // 2
        logo_y = y - logo_img.height // 2
        draw.ellipse([(logo_x - 5, logo_y - 5), (logo_x + logo_img.width + 5, logo_y + logo_img.height + 5)],
                    outline=pal["border"], width=1)
        return logo_img, (logo_x, logo_y)
    else:
        # Если логотип не загружен, рисуем заглушку (книга со свечой)
        book_width = 50
        book_height = 38
        book_x = x - book_width//2
        book_y = y - book_height//2
        
        draw.rectangle([(book_x, book_y), (book_x + book_width, book_y + book_height)], 
                       fill=(255, 255, 255, 200), outline=pal["border"], width=2)
        
        for i in range(3):
            offset = 3 + i * 3
            draw.line([(book_x + offset, book_y + 5), (book_x + offset, book_y + book_height - 5)], 
                      fill=pal["border_light"], width=1)
        
        # Свеча
        candle_x = x + 30
        candle_y = y - 15
        draw.rectangle([(candle_x - 3, candle_y), (candle_x + 3, candle_y + 12)], 
                       fill=(245, 220, 200), outline=pal["border"], width=1)
        draw.line([(candle_x, candle_y), (candle_x, candle_y - 4)], fill=(50, 50, 50), width=1)
        
        for i in range(3):
            flame_size = 4 - i * 1.5
            if flame_size > 0:
                draw.ellipse([(candle_x - flame_size, candle_y - 7 - i * 3),
                             (candle_x + flame_size, candle_y - 3 - i * 3)], 
                            fill=(255, 200, 50, 255 - i * 80))
        
        return None, None


def create_hero_card(hero):
    width, height = 500, 700
    rarity = hero.get("rarity", "обычный")
    is_legendary = (rarity == "легендарный")

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

    img = create_vintage_texture(width, height)
    draw = ImageDraw.Draw(img)

    # Загружаем логотип
    logo_img = load_logo()
    
    # Рамка
    draw_elegant_frame(draw, width, height, pal)

    # Логотип в левом верхнем углу
    logo_result = draw_logo(draw, 55, 40, pal, logo_img)
    if logo_img:
        logo_img_resized, (logo_x, logo_y) = logo_result
        if logo_img_resized:
            img.paste(logo_img_resized, (logo_x, logo_y), logo_img_resized)

    # Заголовок
    y = 38
    font_title = load_font(20, "italic")
    title_text = "✦ Litra Packs ✦"
    draw.text((width//2 + 20, y), title_text, fill=pal["accent"], font=font_title, anchor="mt")
    
    y += 15
    draw_ornament_pattern(draw, width//2 - 80, y, 160, pal, 7)
    y += 30

    # Портрет или обложка
    portrait_y = y
    portrait_size = 170
    
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
            
            draw.ellipse([(x - 6, portrait_y - 6), (x + portrait_size + 6, portrait_y + portrait_size + 6)], 
                         outline=pal["border"], width=2)
            draw.ellipse([(x - 3, portrait_y - 3), (x + portrait_size + 3, portrait_y + portrait_size + 3)], 
                         outline=pal["accent"], width=1)
            
            for angle in range(0, 360, 20):
                rad = math.radians(angle)
                ox = x + portrait_size//2 + int((portrait_size//2 + 12) * math.cos(rad))
                oy = portrait_y + portrait_size//2 + int((portrait_size//2 + 12) * math.sin(rad))
                size = 2 if angle % 40 == 0 else 1
                draw.ellipse([(ox - size, oy - size), (ox + size, oy + size)], fill=pal["accent"])
            
            y = portrait_y + portrait_size + 30
        else:
            y = portrait_y + 190
    else:
        # Для нелегендарных героев - обложка книги
        book_title = hero.get("book", hero.get("work", "Книга"))
        draw_book_illustration(draw, width//2 - 85, portrait_y, 170, 170, pal, book_title)
        y = portrait_y + 190

    # Имя героя
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
        y += 22
        
        quote = get_random_quote(author)
        draw_quote_style(draw, 40, y, quote, pal)
        y += 100
        
        draw_ornament_pattern(draw, width//2 - 50, y - 8, 100, pal, 5)
        draw.text((width//2, y), f"— {author} —", fill=pal["sub"], font=font_info_small, anchor="mt")
        y += 35
    else:
        book = hero.get("book", hero.get("work", "Неизвестное произведение"))
        if len(book) > 30:
            book = book[:27] + "..."
        draw.text((width//2, y), f'«{book}»', fill=pal["sub"], font=font_info, anchor="mt")
        y += 24
        
        draw_ornament_pattern(draw, width//2 - 50, y - 5, 100, pal, 5)
        
        author = hero.get("author", "Неизвестный автор")
        draw.text((width//2, y), f"— {author} —", fill=pal["sub"], font=font_info_small, anchor="mt")
        y += 30

    # Редкость
    draw_rarity_badge(draw, width//2, y, rarity, pal)
    y += 35

    # Декоративный узор внизу
    draw_ornament_pattern(draw, width//2 - 60, height - 48, 120, pal, 7)

    # Футер
    footer_y = height - 22
    font_footer = load_font(11, "italic")
    draw.text((width//2, footer_y), "❧ Из собрания литературных героев ❧", 
             fill=(pal["sub"][0], pal["sub"][1], pal["sub"][2], 180), 
             font=font_footer, anchor="mt")
    
    # Эффекты
    img = img.filter(ImageFilter.GaussianBlur(radius=0.3))
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.4)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.05)

    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=95, optimize=True)
    bio.seek(0)
    return bio