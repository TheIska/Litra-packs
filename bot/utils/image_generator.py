import io
import os
import random
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont

COVERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'covers')
FONTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')

# Прямая ссылка на шрифт
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/playfairdisplay/PlayfairDisplay-Regular.ttf"

# Кэш для шрифта и обложек
_font_cache = None
_cover_cache = {}

def download_font():
    """Скачивает шрифт из интернета, если его нет локально"""
    global _font_cache
    try:
        os.makedirs(FONTS_DIR, exist_ok=True)
        font_path = os.path.join(FONTS_DIR, "regular.ttf")
        if not os.path.exists(font_path):
            urllib.request.urlretrieve(FONT_URL, font_path)
        return font_path
    except:
        return None

def load_font(size):
    """Загружает шрифт (с кэшированием)"""
    global _font_cache
    if _font_cache is not None:
        return _font_cache
    
    font_path = os.path.join(FONTS_DIR, "regular.ttf")
    if not os.path.exists(font_path):
        font_path = download_font()
    
    if font_path and os.path.exists(font_path):
        try:
            _font_cache = ImageFont.truetype(font_path, size)
            return _font_cache
        except:
            pass
    
    _font_cache = ImageFont.load_default()
    return _font_cache

def load_cover(book_name):
    """Загружает обложку книги (с кэшированием)"""
    global _cover_cache
    clean_name = book_name.replace('"', '').replace('«', '').replace('»', '').replace('?', '').replace('!', '')
    
    # Проверяем кэш
    if clean_name in _cover_cache:
        return _cover_cache[clean_name]
    
    # Локально
    extensions = ['.jpg', '.jpeg', '.png', '.webp']
    for ext in extensions:
        path = os.path.join(COVERS_DIR, f"{clean_name}{ext}")
        if os.path.exists(path):
            try:
                img = Image.open(path).convert("RGBA")
                _cover_cache[clean_name] = img
                return img
            except:
                pass
    
    # Через Google Books (с таймаутом 3 секунды)
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{urllib.parse.quote(book_name)}&maxResults=1"
        with urllib.request.urlopen(url, timeout=3) as response:
            data = json.loads(response.read().decode())
            if 'items' in data and len(data['items']) > 0:
                volume = data['items'][0]['volumeInfo']
                if 'imageLinks' in volume:
                    cover_url = volume['imageLinks'].get('thumbnail')
                    if cover_url:
                        with urllib.request.urlopen(cover_url, timeout=3) as img_response:
                            img_data = img_response.read()
                            img = Image.open(io.BytesIO(img_data)).convert("RGBA")
                            try:
                                os.makedirs(COVERS_DIR, exist_ok=True)
                                local_path = os.path.join(COVERS_DIR, f"{clean_name}.jpg")
                                img.save(local_path, 'JPEG')
                            except:
                                pass
                            _cover_cache[clean_name] = img
                            return img
    except:
        pass
    
    _cover_cache[clean_name] = None
    return None

def create_hero_card(hero):
    width, height = 400, 560  # Уменьшенный размер для скорости
    rarity = hero.get("rarity", "обычный")

    colors = {
        "легендарный": {"bg": (45, 35, 25), "border": (255, 215, 0), "accent": (255, 215, 0), "text": (255, 235, 200), "rarity_color": (255, 215, 0), "subtext": (200, 180, 150)},
        "эпический": {"bg": (35, 25, 45), "border": (155, 89, 182), "accent": (155, 89, 182), "text": (255, 235, 200), "rarity_color": (155, 89, 182), "subtext": (200, 180, 150)},
        "редкий": {"bg": (25, 35, 45), "border": (52, 152, 219), "accent": (52, 152, 219), "text": (255, 235, 200), "rarity_color": (52, 152, 219), "subtext": (200, 180, 150)},
        "обычный": {"bg": (35, 35, 35), "border": (149, 165, 166), "accent": (149, 165, 166), "text": (220, 210, 190), "rarity_color": (149, 165, 166), "subtext": (180, 170, 150)}
    }

    pal = colors.get(rarity, colors["обычный"])

    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)

    # Упрощённая текстура (без циклов)
    font = load_font(24)

    # Рамка
    border_width = 6
    draw.rectangle([(border_width, border_width), (width - border_width, height - border_width)], outline=pal["border"], width=3)

    # Заголовок
    draw.text((width//2, 12), "ЛИТЕРАТУРНЫЙ ГЕРОЙ", fill=pal["accent"], font=font, anchor="mt")

    # Обложка (уменьшенная)
    cover_img = load_cover(hero["book"])
    if cover_img:
        cover_img = cover_img.resize((140, 190), Image.Resampling.LANCZOS)
        x = (width - 140) // 2
        y = 45
        img.paste(cover_img, (x, y), cover_img)
        draw.rectangle([(x-3, y-3), (x+143, y+193)], outline=pal["border"], width=2)
        y_offset = 260
    else:
        draw.text((width//2, 120), "📚", fill=pal["border"], font=font, anchor="mt")
        y_offset = 230

    # Имя
    draw.text((width//2 + 1, y_offset + 1), hero["name"], fill=(0,0,0), font=font, anchor="mt")
    draw.text((width//2, y_offset), hero["name"], fill=pal["text"], font=font, anchor="mt")

    y_offset += 40
    draw.line([(40, y_offset), (width - 40, y_offset)], fill=pal["accent"], width=1)
    y_offset += 25

    # Книга
    draw.text((width//2, y_offset), hero["book"], fill=pal["subtext"], font=font, anchor="mt")
    y_offset += 25

    # Автор
    draw.text((width//2, y_offset), hero["author"], fill=pal["subtext"], font=font, anchor="mt")
    y_offset += 35

    # Редкость
    rarity_labels = {"легендарный": "ЛЕГЕНДАРНЫЙ", "эпический": "ЭПИЧЕСКИЙ", "редкий": "РЕДКИЙ", "обычный": "ОБЫЧНЫЙ"}
    draw.text((width//2, y_offset), rarity_labels.get(rarity, "ОБЫЧНЫЙ"), fill=pal["rarity_color"], font=font, anchor="mt")

    draw.text((width//2, height - 15), "С любовью к литературе", fill=(80, 75, 65), font=font, anchor="mt")

    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=85, optimize=True)
    bio.seek(0)
    return bio