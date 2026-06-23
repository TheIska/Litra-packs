# bot/utils/image_generator.py

import io
import os
import random
import math
import traceback
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
    except Exception as e:
        print(f"❌ Ошибка загрузки шрифта: {e}")
        return ImageFont.load_default()


def load_portrait(hero):
    """Загружает портрет для легендарного героя"""
    try:
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
            except Exception as e:
                print(f"❌ Ошибка загрузки портрета: {e}")
                return None
        return None
    except Exception as e:
        print(f"❌ Ошибка в load_portrait: {e}")
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
    try:
        img = Image.new('RGB', (width, height), (245, 240, 230))
        draw = ImageDraw.Draw(img)
        
        for i in range(height):
            ratio = i / height
            dark = int(20 * (1 - abs(ratio - 0.5) * 2))
            draw.line([(0, i), (width, i)], fill=(245 - dark, 240 - dark, 230 - dark))
        
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
    except Exception as e:
        print(f"❌ Ошибка в create_vintage_texture: {e}")
        return Image.new('RGB', (width, height), (245, 240, 230))


def draw_stars(draw, x, y, count, color):
    """Рисует звёздочки для редкости"""
    try:
        for i in range(count):
            star_x = x - (count - 1) * 14 + i * 28
            for angle in range(0, 360, 72):
                rad = math.radians(angle)
                dx = int(8 * math.cos(rad))
                dy = int(8 * math.sin(rad))
                draw.point((star_x + dx, y + dy), fill=color)
            draw.point((star_x, y), fill=color)
    except Exception as e:
        print(f"❌ Ошибка в draw_stars: {e}")


def draw_corner_ornament(draw, x, y, pal, size=15, direction="tl"):
    """Рисует угловой орнамент в нужном направлении"""
    if direction == "tl":
        start_angle, end_angle = 0, 90
    elif direction == "tr":
        start_angle, end_angle = 90, 180
    elif direction == "bl":
        start_angle, end_angle = 270, 360
    else:
        start_angle, end_angle = 180, 270
    
    for i in range(3, 0, -1):
        s = size - (3 - i) * 4
        if s > 4:
            draw.arc([x - s, y - s, x + s, y + s], start_angle, end_angle, 
                     fill=pal["border_light"], width=1)
    
    draw.ellipse([x - 1.5, y - 1.5, x + 1.5, y + 1.5], fill=pal["accent"])


def create_hero_card(hero):
    """Создаёт карточку героя с номером"""
    try:
        print(f"🖼️ create_hero_card вызвана для: {hero.get('name', 'Unknown')}")
        
        width, height = 500, 700
        rarity = hero.get("rarity", "обычный")
        is_legendary = (rarity == "легендарный")
        
        card_number = hero.get('card_number', random.randint(1, 225))

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

        # --- РАМКА ---
        p = 18
        draw.rectangle([(p, p), (width - p, height - p)], outline=pal["border"], width=2)

        # --- НОМЕР КАРТЫ (ЗА РАМКОЙ, В ПРАВЫЙ ВЕРХНИЙ УГОЛ) ---
        font_number = load_font(16, "bold")
        number_text = f"№ {card_number:03d}"
        draw.text((width - 5, 5), number_text, fill=pal["border"], font=font_number, anchor="rt")

        # --- LITRA PACKS (ЗА РАМКОЙ, В ЛЕВЫЙ ВЕРХНИЙ УГОЛ) ---
        font_title = load_font(14, "italic")
        draw.text((5, 8), "Litra Packs", fill=pal["accent"], font=font_title, anchor="lt")

        # --- УГЛОВЫЕ ОРНАМЕНТЫ ---
        corner_size = 18
        draw_corner_ornament(draw, p + 8, p + 8, pal, corner_size, "tl")
        draw_corner_ornament(draw, width - p - 8, p + 8, pal, corner_size, "tr")
        draw_corner_ornament(draw, p + 8, height - p - 8, pal, corner_size, "bl")
        draw_corner_ornament(draw, width - p - 8, height - p - 8, pal, corner_size, "br")

        # --- ОСНОВНОЙ КОНТЕНТ ---
        start_y = 80
        
        if is_legendary:
            content_height = 150 + 25 + 60 + 48 + 30 + 35
        else:
            content_height = 60 + 48 + 30 + 35
        
        content_start = (height - p - 10 - content_height) // 2 + 10
        current_y = content_start

        # --- ПОРТРЕТ (только для легендарных) ---
        if is_legendary:
            portrait_size = 150
            portrait_y = current_y
            
            portrait = load_portrait(hero)
            if portrait:
                portrait = portrait.resize((portrait_size, portrait_size), Image.Resampling.LANCZOS)
                
                mask = Image.new('L', (portrait_size, portrait_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((2, 2, portrait_size - 2, portrait_size - 2), fill=255)
                portrait.putalpha(mask)
                
                x = (width - portrait_size) // 2
                img.paste(portrait, (x, portrait_y), portrait)
                
                draw.ellipse([(x - 4, portrait_y - 4), 
                              (x + portrait_size + 4, portrait_y + portrait_size + 4)], 
                             outline=pal["border"], width=2)
                draw.ellipse([(x - 2, portrait_y - 2), 
                              (x + portrait_size + 2, portrait_y + portrait_size + 2)], 
                             outline=pal["accent"], width=1)
                
                current_y += portrait_size + 25
            else:
                current_y += 150 + 25

        # --- ХАРАКТЕРИСТИКИ (только для нелегендарных) ---
        # МЕЧИ, МОЗГ И СЕРДЦЕ
        if not is_legendary:
            strength = hero.get('strength', random.randint(30, 99))
            intelligence = hero.get('intelligence', random.randint(30, 99))
            kindness = hero.get('kindness', random.randint(30, 99))
            
            font_stats = load_font(42, "bold")
            
            # Символы: ⚔ - меч, 🧠 - мозг, ❤ - сердце
            stats_text = f"⚔ {strength}  🧠 {intelligence}  ❤ {kindness}"
            
            # Поднимаем чуть выше
            center_y = current_y - 10
            
            draw.text((width//2, center_y), stats_text, fill=(0, 0, 0), font=font_stats, anchor="mt")
            
            current_y = center_y + 55

        # --- ИМЯ ГЕРОЯ ---
        y = current_y
        name = hero.get("name", "Неизвестный герой")
        font_name = load_font(38, "bold")
        
        draw.text((width//2 + 1, y + 1), name, fill=(0, 0, 0, 20), font=font_name, anchor="mt")
        draw.text((width//2, y), name, fill=pal["text"], font=font_name, anchor="mt")
        current_y += 48

        # --- НАЗВАНИЕ ПРОИЗВЕДЕНИЯ ---
        y = current_y
        book = hero.get("book", hero.get("work", "Неизвестное произведение"))
        if len(book) > 28:
            book = book[:25] + "..."
        
        font_book = load_font(20, "italic")
        draw.text((width//2, y), f'«{book}»', fill=pal["sub"], font=font_book, anchor="mt")
        current_y += 30

        # --- АВТОР ---
        y = current_y
        author = hero.get("author", "Неизвестный автор")
        font_author = load_font(17, "regular")
        draw.text((width//2, y), f'— {author} —', fill=pal["sub"], font=font_author, anchor="mt")
        current_y += 35

        # --- РЕДКОСТЬ ---
        rarity_y = height - p - 10 - 30
        
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
        
        stars_count = {"легендарный": 5, "эпический": 4, "редкий": 3, "обычный": 2}
        stars = stars_count.get(rarity, 2)
        
        star_y = rarity_y - 5
        draw_stars(draw, width//2, star_y, stars, color)
        
        draw.text((width//2 + 1, rarity_y + 1), rarity_text, fill=(0, 0, 0, 15), font=font_rare, anchor="mt")
        draw.text((width//2, rarity_y), rarity_text, fill=color, font=font_rare, anchor="mt")
        
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.5)
        
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.05)

        bio = io.BytesIO()
        img.save(bio, format='JPEG', quality=95, optimize=True)
        bio.seek(0)
        
        print(f"✅ Карточка создана для {hero.get('name')}")
        return bio
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА в create_hero_card: {e}")
        traceback.print_exc()
        img = Image.new('RGB', (500, 700), (255, 200, 200))
        draw = ImageDraw.Draw(img)
        draw.text((250, 350), "Ошибка создания карточки", fill=(0, 0, 0), anchor="mt")
        bio = io.BytesIO()
        img.save(bio, format='JPEG', quality=95)
        bio.seek(0)
        return bio