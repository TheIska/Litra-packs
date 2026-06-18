import io
import os
import random
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont

def load_font(size, style="regular"):
    """Загружает шрифт из папки static/fonts"""
    try:
        font_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')
        
        font_files = {
            "regular": "regular.ttf",
            "italic": "italic.ttf",
            "bold": "bold.ttf"
        }
        
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

def get_years(author):
    """Возвращает годы жизни для автора"""
    years = {
        "А.С. Пушкин": "1799–1837",
        "М.Ю. Лермонтов": "1814–1841",
        "Н.В. Гоголь": "1809–1852",
        "Ф.М. Достоевский": "1821–1881",
        "И.С. Тургенев": "1818–1883",
    }
    return years.get(author, "")

def get_random_quote(author):
    """Возвращает случайную цитату для автора"""
    quotes = {
        "А.С. Пушкин": [
            "Я жить хочу, чтоб мыслить и страдать.",
            "Гений и злодейство — две вещи несовместимые.",
            "Вдохновение — это умение приводить себя в рабочее состояние.",
            "Привычка свыше нам дана, замена счастию она.",
            "Мой друг, отчизне посвятим души прекрасные порывы!"
        ],
        "М.Ю. Лермонтов": [
            "Гений, прикованный к чиновничьему столу, должен умереть или сойти с ума.",
            "Поверь мне — счастье только там, где любят нас, где верят нам!",
            "Из двух друзей всегда один раб другого.",
            "Я люблю сомневаться во всем.",
            "Герой не тот, кто победил, а тот, кто не сдался."
        ],
        "Н.В. Гоголь": [
            "Какой же русский не любит быстрой езды?",
            "Есть у русского человека враг — лень.",
            "Нет слова, которое было бы так замашисто, как метко сказанное русское слово.",
            "Обращаться со словами нужно честно.",
            "В каждом слове бездна пространства."
        ],
        "Ф.М. Достоевский": [
            "Человек есть тайна. Ее надо разгадывать всю жизнь.",
            "Если Бога нет, то всё позволено.",
            "Красота спасет мир.",
            "Станьте солнцем, вас все и увидят.",
            "Безответная любовь не унижает человека, а возвышает его."
        ],
        "И.С. Тургенев": [
            "Во дни сомнений, во дни тягостных раздумий о судьбах моей родины, — ты один мне поддержка, о русский язык!",
            "Любовь сильнее смерти и страха смерти.",
            "Счастье — как здоровье: когда его не замечаешь, значит, оно есть.",
            "Нет ничего тягостнее сознания только что сделанной глупости.",
            "Добро по указу — не добро."
        ]
    }
    
    author_quotes = quotes.get(author, ["С любовью к литературе"])
    return random.choice(author_quotes)

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
    
    filename = portrait_map.get(hero["name"])
    if not filename:
        return None
    
    portrait_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'portraits', filename)
    if os.path.exists(portrait_path):
        try:
            return Image.open(portrait_path).convert("RGBA")
        except:
            return None
    return None

def create_hero_card(hero):
    """Создаёт карточку героя"""
    width, height = 500, 700
    rarity = hero.get("rarity", "обычный")
    is_legendary = (rarity == "легендарный")
    author = hero.get("author", "")

    # Цвета
    colors = {
        "легендарный": {
            "bg": (35, 25, 15),
            "border": (255, 215, 0),
            "accent": (255, 215, 0),
            "text": (255, 240, 220),
            "rare": (255, 215, 0),
            "sub": (200, 180, 150),
            "bg2": (50, 40, 30)
        },
        "эпический": {
            "bg": (25, 15, 35),
            "border": (155, 89, 182),
            "accent": (155, 89, 182),
            "text": (255, 240, 220),
            "rare": (155, 89, 182),
            "sub": (200, 180, 150),
            "bg2": (45, 30, 55)
        },
        "редкий": {
            "bg": (15, 25, 35),
            "border": (52, 152, 219),
            "accent": (52, 152, 219),
            "text": (255, 240, 220),
            "rare": (52, 152, 219),
            "sub": (200, 180, 150),
            "bg2": (30, 45, 55)
        },
        "обычный": {
            "bg": (30, 30, 30),
            "border": (150, 160, 170),
            "accent": (150, 160, 170),
            "text": (220, 210, 190),
            "rare": (150, 160, 170),
            "sub": (180, 170, 150),
            "bg2": (50, 50, 50)
        }
    }

    pal = colors.get(rarity, colors["обычный"])

    # ФОН С ГРАДИЕНТОМ
    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)
    
    for i in range(height):
        ratio = i / height
        r = int(pal["bg"][0] * (1 - ratio) + pal["bg2"][0] * ratio)
        g = int(pal["bg"][1] * (1 - ratio) + pal["bg2"][1] * ratio)
        b = int(pal["bg"][2] * (1 - ratio) + pal["bg2"][2] * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # Шрифты
    font_title = load_font(28, "bold")
    font_name = load_font(44, "bold")
    font_rare = load_font(28, "bold")
    font_footer = load_font(18, "italic")
    font_quote = load_font(16, "italic")
    font_years = load_font(18, "italic")
    font_book = load_font(24, "regular")
    font_author_style = load_font(22, "italic")

    # РАМКА
    border = 8
    draw.rectangle([(border, border), (width - border, height - border)], outline=pal["border"], width=3)
    draw.rectangle([(border + 12, border + 12), (width - border - 12, height - border - 12)], outline=pal["border"], width=1)

    # ЗАГОЛОВОК
    draw.text((width//2, 22), "LITRA PACKS", fill=pal["accent"], font=font_title, anchor="mt")

    # РАЗДЕЛИТЕЛЬ
    y = 55
    draw.line([(60, y), (width - 60, y)], fill=pal["border"], width=1)
    y += 30

    # ПОРТРЕТ (только для легендарных)
    portrait = None
    if is_legendary:
        portrait = load_portrait(hero)
        if portrait:
            portrait = portrait.resize((180, 180), Image.Resampling.LANCZOS)
            mask = Image.new('L', (180, 180), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 180, 180), fill=255)
            portrait.putalpha(mask)
            x = (width - 180) // 2
            y_portrait = 70
            img.paste(portrait, (x, y_portrait), portrait)
            draw.ellipse([(x-5, y_portrait-5), (x+185, y_portrait+185)], outline=pal["border"], width=4)
            name_y = 290
        else:
            name_y = height // 2 - 50
    else:
        # Для не-легендарных обложка
        cover_img = load_cover(hero["book"])
        if cover_img:
            cover_img = cover_img.resize((130, 190), Image.Resampling.LANCZOS)
            x = (width - 130) // 2
            y_cover = 90
            img.paste(cover_img, (x, y_cover), cover_img)
            draw.rectangle([(x-3, y_cover-3), (x+133, y_cover+193)], outline=pal["border"], width=2)
            name_y = 310
        else:
            name_y = height // 2 - 50

    # ИМЯ ГЕРОЯ
    name = hero["name"]
    for dx, dy in [(-3,-3), (-3,3), (3,-3), (3,3)]:
        draw.text((width//2 + dx, name_y + dy), name, fill=(0, 0, 0), font=font_name, anchor="mt")
    draw.text((width//2, name_y), name, fill=pal["text"], font=font_name, anchor="mt")

    # РАЗДЕЛИТЕЛЬ
    y = name_y + 50
    draw.line([(60, y), (width - 60, y)], fill=pal["accent"], width=1)
    y += 35

    # ДЛЯ ЛЕГЕНДАРНЫХ: годы жизни и цитата
    if is_legendary and portrait:
        # Годы жизни
        years = get_years(hero.get("author", ""))
        draw.text((width//2, y), years, fill=pal["sub"], font=font_years, anchor="mt")
        y += 32
        
        # Цитата
        quote = get_random_quote(hero.get("author", ""))
        words = quote.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 35:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        for i, line in enumerate(lines):
            draw.text((width//2, y + i * 22), f'"{line}"', fill=pal["sub"], font=font_quote, anchor="mt")
        
        y += len(lines) * 22 + 35
        footer_y = height - 22
    else:
        # ДЛЯ НЕ ЛЕГЕНДАРНЫХ: книга и автор
        book = hero["book"]
        draw.text((width//2, y), f'"{book}"', fill=pal["sub"], font=font_book, anchor="mt")
        y += 30
        author = hero["author"]
        draw.text((width//2, y), author, fill=pal["sub"], font=font_author_style, anchor="mt")
        y += 35
        footer_y = height - 22

    # РЕДКОСТЬ
    rare_labels = {
        "легендарный": "ЛЕГЕНДАРНЫЙ",
        "эпический": "ЭПИЧЕСКИЙ",
        "редкий": "РЕДКИЙ",
        "обычный": "ОБЫЧНЫЙ"
    }
    rare_text = rare_labels.get(rarity, "ОБЫЧНЫЙ")
    draw.text((width//2, y), rare_text, fill=pal["rare"], font=font_rare, anchor="mt")

    # НИЖНИЙ КОЛОНТИТУЛ
    draw.text((width//2, footer_y), "С любовью к литературе", fill=(80, 75, 65), font=font_footer, anchor="mt")

    # Сохраняем
    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=92, optimize=True)
    bio.seek(0)
    return bio