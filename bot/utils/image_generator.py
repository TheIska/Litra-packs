import io
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont
import json

# Путь к папкам
COVERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'covers')
FONTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')

# Ссылка на шрифт в стиле XVIII века (Google Fonts: Playfair Display — старинный, с засечками)
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Regular.ttf"
FONT_ITALIC_URL = "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Italic.ttf"
FONT_BOLD_URL = "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Bold.ttf"

def download_font(url, filename):
    """Скачивает шрифт из интернета"""
    try:
        os.makedirs(FONTS_DIR, exist_ok=True)
        path = os.path.join(FONTS_DIR, filename)
        if os.path.exists(path):
            return path
        urllib.request.urlretrieve(url, path)
        return path
    except:
        return None

def load_font(size, italic=False, bold=False):
    """Загружает шрифт в стиле XVIII века"""
    try:
        if bold:
            filename = "PlayfairDisplay-Bold.ttf"
            url = FONT_BOLD_URL
        elif italic:
            filename = "PlayfairDisplay-Italic.ttf"
            url = FONT_ITALIC_URL
        else:
            filename = "PlayfairDisplay-Regular.ttf"
            url = FONT_URL
        
        font_path = os.path.join(FONTS_DIR, filename)
        if not os.path.exists(font_path):
            font_path = download_font(url, filename)
            if not font_path:
                return ImageFont.load_default()
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()

def load_cover(book_name):
    """Загружает обложку книги: сначала локально, потом из интернета через Google Books API"""
    clean_name = book_name.replace('"', '').replace('«', '').replace('»', '').replace('?', '').replace('!', '')
    
    # 1. Пробуем локально
    extensions = ['.jpg', '.jpeg', '.png', '.webp']
    for ext in extensions:
        path = os.path.join(COVERS_DIR, f"{clean_name}{ext}")
        if os.path.exists(path):
            try:
                return Image.open(path).convert("RGBA")
            except:
                pass
    
    # 2. Ищем через Google Books API
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{urllib.parse.quote(book_name)}&maxResults=1"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            if 'items' in data and len(data['items']) > 0:
                volume = data['items'][0]['volumeInfo']
                if 'imageLinks' in volume:
                    cover_url = volume['imageLinks'].get('thumbnail')
                    if cover_url:
                        with urllib.request.urlopen(cover_url, timeout=5) as img_response:
                            img_data = img_response.read()
                            img = Image.open(io.BytesIO(img_data)).convert("RGBA")
                            try:
                                os.makedirs(COVERS_DIR, exist_ok=True)
                                local_path = os.path.join(COVERS_DIR, f"{clean_name}.jpg")
                                img.save(local_path, 'JPEG')
                            except:
                                pass
                            return img
    except Exception as e:
        print(f"Не удалось загрузить обложку для {book_name}: {e}")
    
    return None

def create_hero_card(hero):
    """Создаёт карточку героя в стиле XVIII века"""
    width, height = 500, 700
    rarity = hero.get("rarity", "обычный")

    # Цвета в стиле старой книги (пергамент, золото)
    colors = {
        "легендарный": {
            "bg": (45, 35, 25),
            "border": (255, 215, 0),
            "accent": (255, 215, 0),
            "text": (255, 235, 200),
            "rarity_color": (255, 215, 0),
            "subtext": (200, 180, 150)
        },
        "эпический": {
            "bg": (35, 25, 45),
            "border": (155, 89, 182),
            "accent": (155, 89, 182),
            "text": (255, 235, 200),
            "rarity_color": (155, 89, 182),
            "subtext": (200, 180, 150)
        },
        "редкий": {
            "bg": (25, 35, 45),
            "border": (52, 152, 219),
            "accent": (52, 152, 219),
            "text": (255, 235, 200),
            "rarity_color": (52, 152, 219),
            "subtext": (200, 180, 150)
        },
        "обычный": {
            "bg": (35, 35, 35),
            "border": (149, 165, 166),
            "accent": (149, 165, 166),
            "text": (220, 210, 190),
            "rarity_color": (149, 165, 166),
            "subtext": (180, 170, 150)
        }
    }

    pal = colors.get(rarity, colors["обычный"])

    # Создаём фон (с эффектом старой бумаги)
    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)

    # Добавляем текстуру "старой бумаги" (лёгкий шум)
    for i in range(0, height, 3):
        for j in range(0, width, 3):
            noise = random.randint(-10, 10)
            r = max(0, min(255, pal["bg"][0] + noise))
            g = max(0, min(255, pal["bg"][1] + noise))
            b = max(0, min(255, pal["bg"][2] + noise))
            draw.point((j, i), fill=(r, g, b))

    # Шрифты в стиле XVIII века
    font_title = load_font(20, italic=True)
    font_name = load_font(34, bold=True)
    font_book = load_font(18, italic=True)
    font_author = load_font(16, italic=True)
    font_rarity = load_font(24, bold=True)
    font_footer = load_font(12, italic=True)

    # Рамка с орнаментом
    border_width = 8
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=pal["border"],
        width=3
    )
    # Внутренняя рамка (тонкая)
    draw.rectangle(
        [(border_width + 10, border_width + 10), (width - border_width - 10, height - border_width - 10)],
        outline=pal["accent"],
        width=1
    )

    # Заголовок (вензель)
    draw.text((width//2, 12), "Литературный Герой", fill=pal["accent"], font=font_title, anchor="mt")

    # Декоративный разделитель
    for i in range(10):
        x = 70 + i * 40
        draw.text((x, 38), "✦", fill=pal["accent"], font=load_font(14))

    # Обложка книги
    cover_img = load_cover(hero["book"])
    if cover_img:
        cover_img = cover_img.resize((170, 240), Image.Resampling.LANCZOS)
        x = (width - 170) // 2
        y = 55
        img.paste(cover_img, (x, y), cover_img)
        # Рамка с золотым тиснением
        draw.rectangle([(x-4, y-4), (x+174, y+244)], outline=pal["border"], width=2)
    else:
        draw.text((width//2, 140), "📜", fill=pal["border"], font=load_font(80), anchor="mt")

    # Имя героя (с тенью для эффекта тиснения)
    y_offset = 330
    # Тень
    draw.text((width//2 + 2, y_offset + 2), hero["name"], fill=(0,0,0), font=font_name, anchor="mt")
    # Основной текст
    draw.text((width//2, y_offset), hero["name"], fill=pal["text"], font=font_name, anchor="mt")

    # Вензель-разделитель
    y_offset += 50
    draw.text((width//2, y_offset), "❧", fill=pal["accent"], font=load_font(24), anchor="mt")
    y_offset += 10
    draw.line([(60, y_offset), (width - 60, y_offset)], fill=pal["accent"], width=1)
    y_offset += 25

    # Книга
    draw.text((width//2, y_offset), f"«{hero['book']}»", fill=pal["subtext"], font=font_book, anchor="mt")
    y_offset += 30

    # Автор
    draw.text((width//2, y_offset), hero["author"], fill=pal["subtext"], font=font_author, anchor="mt")
    y_offset += 45

    # Редкость
    rarity_labels = {
        "легендарный": "✦ ЛЕГЕНДАРНЫЙ ✦",
        "эпический": "✦ ЭПИЧЕСКИЙ ✦",
        "редкий": "✦ РЕДКИЙ ✦",
        "обычный": "✦ ОБЫЧНЫЙ ✦"
    }
    rarity_text = rarity_labels.get(rarity, "✦ ОБЫЧНЫЙ ✦")
    draw.text((width//2, y_offset), rarity_text, fill=pal["rarity_color"], font=font_rarity, anchor="mt")

    # Вензель внизу
    y_offset += 45
    draw.text((width//2, height - 22), "† С любовью к литературе †", fill=(80, 75, 65), font=font_footer, anchor="mt")

    bio = io.BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio

import random  # для шума на фоне