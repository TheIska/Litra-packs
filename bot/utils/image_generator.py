import io
import os
import random
import math
import traceback
from PIL import Image, ImageDraw, ImageFont, ImageEnhance


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
    except Exception as e:
        print(f"❌ Ошибка загрузки шрифта: {e}")
        return ImageFont.load_default()


def load_portrait(hero):
    try:
        if hero.get("rarity") != "легендарный":
            return None
        
        portrait_map = {
            "Пушкин": "pushkin.png",
            "Лермонтов": "lermontov.png",
            "Гоголь": "gogol.png",
            "Тургенев": "turgenev.png",
            "Достоевский": "dostoevsky.png",
        }
        
        hero_name = hero.get("name", "")
        author = hero.get("author", "")
        
        for key, value in portrait_map.items():
            if key in hero_name or hero_name in key or key in author or author in key:
                portrait_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'portraits', value)
                if os.path.exists(portrait_path):
                    try:
                        return Image.open(portrait_path).convert("RGBA")
                    except:
                        return None
        return None
    except:
        return None


def get_years(author):
    years = {
        "Пушкин": "1799–1837",
        "Лермонтов": "1814–1841",
        "Гоголь": "1809–1852",
        "Тургенев": "1818–1883",
        "Достоевский": "1821–1881",
    }
    for key, value in years.items():
        if key in author:
            return value
    return ""


def create_vintage_texture(width, height):
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
    except:
        return Image.new('RGB', (width, height), (245, 240, 230))


def draw_stars(draw, x, y, count, color):
    try:
        for i in range(count):
            star_x = x - (count - 1) * 14 + i * 28
            for angle in range(0, 360, 72):
                rad = math.radians(angle)
                dx = int(8 * math.cos(rad))
                dy = int(8 * math.sin(rad))
                draw.point((star_x + dx, y + dy), fill=color)
            draw.point((star_x, y), fill=color)
    except:
        pass


def get_center_text_position(draw, text, font, center_x, center_y):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = center_x - text_width // 2
    y = center_y - text_height // 2
    return x, y


def create_hero_card(hero):
    try:
        print(f"🖼️ create_hero_card вызвана для: {hero.get('name', 'Unknown')}")
        
        width, height = 500, 700
        rarity = hero.get("rarity", "обычный")
        is_legendary = (rarity == "легендарный")
        card_number = hero.get('card_number', random.randint(1, 225))

        colors = {
            "легендарный": {
                "border": (180, 130, 70),
                "accent": (200, 150, 70),
                "text": (60, 40, 25),
                "sub": (100, 75, 50)
            },
            "эпический": {
                "border": (140, 105, 155),
                "accent": (160, 120, 170),
                "text": (55, 40, 65),
                "sub": (95, 75, 105)
            },
            "редкий": {
                "border": (85, 130, 165),
                "accent": (95, 145, 175),
                "text": (40, 50, 65),
                "sub": (75, 95, 115)
            },
            "обычный": {
                "border": (130, 120, 110),
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

        # --- НОМЕР КАРТЫ (правый верхний) ---
        font_number = load_font(16, "bold")
        draw.text((width - 10, 10), f"№ {card_number:03d}", fill=pal["border"], font=font_number, anchor="rt")

        # --- LITRA PACKS (левый верхний) ---
        font_title = load_font(14, "bold")
        draw.text((10, 10), "✦ Litra Packs", fill=pal["accent"], font=font_title, anchor="lt")

        # --- СТАТЫ (НАВЕРХУ) ---
        stats_y = 55
        strength = hero.get('strength', random.randint(30, 99))
        intelligence = hero.get('intelligence', random.randint(30, 99))
        kindness = hero.get('kindness', random.randint(30, 99))
        
        font_stats = load_font(32, "bold")
        third = width // 3
        
        draw.text((third // 2, stats_y), f"⚔ {strength}", fill=(0, 0, 0), font=font_stats, anchor="mt")
        draw.text((third + third // 2, stats_y), f"🧠 {intelligence}", fill=(0, 0, 0), font=font_stats, anchor="mt")
        draw.text((third * 2 + third // 2, stats_y), f"❤ {kindness}", fill=(0, 0, 0), font=font_stats, anchor="mt")

        # --- ПОРТРЕТ (для легендарных) ---
        if is_legendary:
            portrait_size = 160
            portrait = load_portrait(hero)
            
            if portrait:
                portrait = portrait.resize((portrait_size, portrait_size), Image.Resampling.LANCZOS)
                mask = Image.new('L', (portrait_size, portrait_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((2, 2, portrait_size - 2, portrait_size - 2), fill=255)
                portrait.putalpha(mask)
                
                portrait_x = (width - portrait_size) // 2
                portrait_y = 110
                img.paste(portrait, (portrait_x, portrait_y), portrait)
                
                draw.ellipse([(portrait_x - 5, portrait_y - 5), 
                              (portrait_x + portrait_size + 5, portrait_y + portrait_size + 5)], 
                             outline=pal["border"], width=2)
                center_y = portrait_y + portrait_size + 50
            else:
                center_y = 160
        else:
            center_y = 150

        # --- ОСНОВНОЙ БЛОК (ИМЯ, КНИГА, АВТОР - ПО ЦЕНТРУ ВЕРТИКАЛИ И ГОРИЗОНТАЛИ) ---
        center_x = width // 2

        # --- ИМЯ ГЕРОЯ ---
        name = hero.get("name", "Неизвестный герой")
        font_name = load_font(36, "bold")
        name_x, name_y = get_center_text_position(draw, name, font_name, center_x, center_y)
        
        draw.text((name_x + 2, name_y + 2), name, fill=(0, 0, 0, 20), font=font_name)
        draw.text((name_x, name_y), name, fill=pal["text"], font=font_name)
        
        bbox = draw.textbbox((0, 0), name, font=font_name)
        name_height = bbox[3] - bbox[1]
        current_y = name_y + name_height + 12

        # --- НАЗВАНИЕ ПРОИЗВЕДЕНИЯ ---
        book = hero.get("book", hero.get("work", "Неизвестное произведение"))
        if len(book) > 30:
            book = book[:27] + "..."
        
        font_book = load_font(20, "italic")
        book_x, book_y = get_center_text_position(draw, f'«{book}»', font_book, center_x, current_y)
        draw.text((book_x, book_y), f'«{book}»', fill=pal["sub"], font=font_book)
        
        bbox = draw.textbbox((0, 0), f'«{book}»', font=font_book)
        book_height = bbox[3] - bbox[1]
        current_y = book_y + book_height + 10

        # --- АВТОР ---
        author = hero.get("author", "Неизвестный автор")
        font_author = load_font(18, "regular")
        
        years = get_years(author)
        author_text = f'— {author}'
        if years:
            author_text += f' ({years})'
        author_text += ' —'
        
        author_x, author_y = get_center_text_position(draw, author_text, font_author, center_x, current_y)
        draw.text((author_x, author_y), author_text, fill=pal["sub"], font=font_author)

        # --- РЕДКОСТЬ (внизу) ---
        rarity_y = height - 45
        
        labels = {
            "легендарный": "ЛЕГЕНДАРНЫЙ",
            "эпический": "ЭПИЧЕСКИЙ",
            "редкий": "РЕДКИЙ",
            "обычный": "ОБЫЧНЫЙ"
        }
        rarity_text = labels.get(rarity, "ОБЫЧНЫЙ")
        font_rare = load_font(20, "bold")
        
        colors_rare = {
            "легендарный": (200, 160, 80),
            "эпический": (160, 120, 170),
            "редкий": (100, 150, 180),
            "обычный": (150, 140, 130)
        }
        color = colors_rare.get(rarity, (150, 140, 130))
        
        stars_count = {"легендарный": 5, "эпический": 4, "редкий": 3, "обычный": 2}
        stars = stars_count.get(rarity, 2)
        
        draw_stars(draw, width//2, rarity_y - 8, stars, color)
        draw.text((width//2 + 1, rarity_y + 1), rarity_text, fill=(0, 0, 0, 15), font=font_rare, anchor="mt")
        draw.text((width//2, rarity_y), rarity_text, fill=color, font=font_rare, anchor="mt")
        
        # --- УЛУЧШЕНИЕ КАЧЕСТВА ---
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