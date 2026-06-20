import io
import os
import random
from PIL import Image, ImageDraw, ImageFont

def load_font(size, style="regular"):
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
    """Загружает портрет для легендарного героя (только те, что есть)"""
    if hero.get("rarity") != "легендарный":
        return None
    
    # Только 5 писателей, для которых есть портреты
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


def create_hero_card(hero):
    width, height = 400, 560
    rarity = hero.get("rarity", "обычный")
    is_legendary = (rarity == "легендарный")

    colors = {
        "легендарный": {"bg": (35, 25, 15), "border": (255, 215, 0), "accent": (255, 215, 0), "text": (255, 240, 220), "rare": (255, 215, 0), "sub": (200, 180, 150), "bg2": (50, 40, 30)},
        "эпический": {"bg": (25, 15, 35), "border": (155, 89, 182), "accent": (155, 89, 182), "text": (255, 240, 220), "rare": (155, 89, 182), "sub": (200, 180, 150), "bg2": (45, 30, 55)},
        "редкий": {"bg": (15, 25, 35), "border": (52, 152, 219), "accent": (52, 152, 219), "text": (255, 240, 220), "rare": (52, 152, 219), "sub": (200, 180, 150), "bg2": (30, 45, 55)},
        "обычный": {"bg": (30, 30, 30), "border": (150, 160, 170), "accent": (150, 160, 170), "text": (220, 210, 190), "rare": (150, 160, 170), "sub": (180, 170, 150), "bg2": (50, 50, 50)}
    }

    pal = colors.get(rarity, colors["обычный"])

    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)
    
    for i in range(height):
        ratio = i / height
        r = int(pal["bg"][0] * (1 - ratio) + pal["bg2"][0] * ratio)
        g = int(pal["bg"][1] * (1 - ratio) + pal["bg2"][1] * ratio)
        b = int(pal["bg"][2] * (1 - ratio) + pal["bg2"][2] * ratio)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    font_title = load_font(22, "bold")
    font_name = load_font(34, "bold")
    font_rare = load_font(22, "bold")
    font_footer = load_font(14, "italic")
    font_quote = load_font(14, "italic")
    font_years = load_font(16, "italic")
    font_book = load_font(18, "regular")
    font_author = load_font(16, "italic")

    border = 6
    draw.rectangle([(border, border), (width - border, height - border)], outline=pal["border"], width=3)
    draw.rectangle([(border + 8, border + 8), (width - border - 8, height - border - 8)], outline=pal["border"], width=1)

    draw.text((width//2, 16), "LITRA PACKS", fill=pal["accent"], font=font_title, anchor="mt")

    y = 45
    draw.line([(40, y), (width - 40, y)], fill=pal["border"], width=1)
    y += 25

    portrait = None
    if is_legendary:
        portrait = load_portrait(hero)
        if portrait:
            portrait = portrait.resize((130, 130), Image.Resampling.LANCZOS)
            mask = Image.new('L', (130, 130), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 130, 130), fill=255)
            portrait.putalpha(mask)
            x = (width - 130) // 2
            y_portrait = 55
            img.paste(portrait, (x, y_portrait), portrait)
            draw.ellipse([(x-4, y_portrait-4), (x+134, y_portrait+134)], outline=pal["border"], width=3)
            name_y = 215
        else:
            name_y = height // 2 - 40
    else:
        name_y = height // 2 - 40

    name = hero["name"]
    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
        draw.text((width//2 + dx, name_y + dy), name, fill=(0, 0, 0), font=font_name, anchor="mt")
    draw.text((width//2, name_y), name, fill=pal["text"], font=font_name, anchor="mt")

    y = name_y + 45
    draw.line([(30, y), (width - 30, y)], fill=pal["accent"], width=1)
    y += 30

    if is_legendary and portrait:
        years = get_years(hero.get("author", ""))
        draw.text((width//2, y), years, fill=pal["sub"], font=font_years, anchor="mt")
        y += 25
        
        quote = get_random_quote(hero.get("author", ""))
        words = quote.split()
        lines = []
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 30:
                current_line += word + " "
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())
        
        for i, line in enumerate(lines):
            draw.text((width//2, y + i * 18), f'"{line}"', fill=pal["sub"], font=font_quote, anchor="mt")
        
        y += len(lines) * 18 + 20
        footer_y = height - 16
    else:
        book = hero["book"]
        if len(book) > 25:
            book = book[:22] + "..."
        draw.text((width//2, y), f'"{book}"', fill=pal["sub"], font=font_book, anchor="mt")
        y += 24
        author = hero["author"]
        draw.text((width//2, y), author, fill=pal["sub"], font=font_author, anchor="mt")
        y += 26
        footer_y = height - 16

    rare_labels = {"легендарный": "ЛЕГЕНДАРНЫЙ", "эпический": "ЭПИЧЕСКИЙ", "редкий": "РЕДКИЙ", "обычный": "ОБЫЧНЫЙ"}
    rare_text = rare_labels.get(rarity, "ОБЫЧНЫЙ")
    
    if is_legendary:
        draw.text((width//2, y - 1), rare_text, fill=(255, 215, 0, 100), font=font_rare, anchor="mt")
    draw.text((width//2, y), rare_text, fill=pal["rare"], font=font_rare, anchor="mt")

    draw.text((width//2, footer_y), "С любовью к литературе", fill=(80, 75, 65), font=font_footer, anchor="mt")

    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=85, optimize=True)
    bio.seek(0)
    return bio