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


def draw_vintage_ornament(draw, x, y, pal):
    """Рисует маленький винтажный орнамент"""
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        dx = int(8 * math.cos(rad))
        dy = int(8 * math.sin(rad))
        draw.point((x + dx, y + dy), fill=pal["border"])
    
    draw.ellipse([(x - 2, y - 2), (x + 2, y + 2)], fill=pal["accent"])
    
    for angle in range(30, 360, 60):
        rad = math.radians(angle)
        dx = int(13 * math.cos(rad))
        dy = int(13 * math.sin(rad))
        draw.point((x + dx, y + dy), fill=pal["border_light"])


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

        # Рамка карты
        p = 18
        draw.rectangle([(p, p), (width - p, height - p)], outline=pal["border"], width=2)
        draw.rectangle([(p + 4, p + 4), (width - p - 4, height - p - 4)], outline=pal["border_light"], width=1)

        # Номер карты
        font_number = load_font(18, "bold")
        number_text = f"№ {card_number:03d}"
        draw.text((width - 30, 25), number_text, fill=pal["border"], font=font_number, anchor="rt")

        # --- РАСЧЁТ ЦЕНТРА ---
        # Вычисляем общую высоту всех блоков
        blocks = []
        
        # Заголовок
        blocks.append(("title", 30))
        
        # Портрет (если есть)
        if is_legendary:
            blocks.append(("portrait", 160))
            blocks.append(("spacer", 20))
        
        # Имя
        blocks.append(("name", 50))
        
        # Книга
        blocks.append(("book", 30))
        
        # Автор
        blocks.append(("author", 30))
        
        # Орнамент
        blocks.append(("ornament", 30))
        
        # Редкость
        blocks.append(("rarity", 35))
        
        # Футер
        blocks.append(("footer", 25))
        
        # Вычисляем общую высоту
        total_height = sum([b[1] for b in blocks])
        
        # Находим стартовую позицию для центрирования
        start_y = (height - total_height) // 2
        
        current_y = start_y

        # --- ЗАГОЛОВОК ---
        y = current_y
        font_title = load_font(22, "italic")
        draw.text((width//2, y), "Litra Packs", fill=pal["accent"], font=font_title, anchor="mt")
        current_y += 30
        
        # Линия под заголовком
        line_y = current_y - 5
        draw.line([(150, line_y), (width - 150, line_y)], fill=pal["border_light"], width=1)
        current_y += 5

        # --- ПОРТРЕТ (только для легендарных) ---
        if is_legendary:
            portrait_size = 160
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
                
                margin = 4
                draw.ellipse([(x - margin, portrait_y - margin), 
                              (x + portrait_size + margin, portrait_y + portrait_size + margin)], 
                             outline=pal["border"], width=2)
                
                draw.ellipse([(x + 2, portrait_y + 2), 
                              (x + portrait_size - 2, portrait_y + portrait_size - 2)], 
                             outline=pal["accent"], width=1)
                
                current_y += portrait_size + 20
            else:
                current_y += 160 + 20

        # --- ИМЯ ГЕРОЯ ---
        y = current_y
        name = hero.get("name", "Неизвестный герой")
        font_name = load_font(44, "bold")
        
        draw.text((width//2 + 1, y + 1), name, fill=(0, 0, 0, 20), font=font_name, anchor="mt")
        draw.text((width//2, y), name, fill=pal["text"], font=font_name, anchor="mt")
        current_y += 50

        # --- НАЗВАНИЕ ПРОИЗВЕДЕНИЯ ---
        y = current_y
        book = hero.get("book", hero.get("work", "Неизвестное произведение"))
        if len(book) > 28:
            book = book[:25] + "..."
        
        font_book = load_font(24, "italic")
        draw.text((width//2, y), f'«{book}»', fill=pal["sub"], font=font_book, anchor="mt")
        current_y += 30

        # --- АВТОР ---
        y = current_y
        author = hero.get("author", "Неизвестный автор")
        font_author = load_font(20, "regular")
        draw.text((width//2, y), f'— {author} —', fill=pal["sub"], font=font_author, anchor="mt")
        current_y += 30

        # --- ОРНАМЕНТ ---
        y = current_y
        draw_vintage_ornament(draw, width//2, y, pal)
        current_y += 30

        # --- РЕДКОСТЬ ---
        y = current_y
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
        
        star_y = y - 3
        draw_stars(draw, width//2, star_y, stars, color)
        
        draw.text((width//2 + 1, y + 1), rarity_text, fill=(0, 0, 0, 15), font=font_rare, anchor="mt")
        draw.text((width//2, y), rarity_text, fill=color, font=font_rare, anchor="mt")
        current_y += 35

        # --- ФУТЕР ---
        y = current_y
        font_footer = load_font(13, "italic")
        draw.text((width//2, y), "Из собрания литературных героев", 
                 fill=(pal["sub"][0], pal["sub"][1], pal["sub"][2], 160), 
                 font=font_footer, anchor="mt")
        
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