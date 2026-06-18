import io
import os
import urllib.request
import urllib.error
from PIL import Image, ImageDraw, ImageFont
import json

# Путь к папкам
COVERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'covers')
FONTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')

def load_font(size):
    """Загружает шрифт с поддержкой кириллицы"""
    try:
        if os.path.exists(FONTS_DIR):
            for f in os.listdir(FONTS_DIR):
                if f.endswith('.ttf') or f.endswith('.otf'):
                    return ImageFont.truetype(os.path.join(FONTS_DIR, f), size)
        return ImageFont.load_default()
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
    
    # 2. Ищем через Google Books API (через urllib)
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
    """Создаёт карточку героя с обложкой книги"""
    width, height = 500, 700
    rarity = hero.get("rarity", "обычный")

    colors = {
        "легендарный": {"bg": (30, 20, 15), "border": (255, 215, 0), "accent": (255, 215, 0), "text": (255, 255, 255), "rarity_color": (255, 215, 0)},
        "эпический": {"bg": (25, 15, 40), "border": (155, 89, 182), "accent": (155, 89, 182), "text": (255, 255, 255), "rarity_color": (155, 89, 182)},
        "редкий": {"bg": (15, 25, 40), "border": (52, 152, 219), "accent": (52, 152, 219), "text": (255, 255, 255), "rarity_color": (52, 152, 219)},
        "обычный": {"bg": (30, 30, 30), "border": (149, 165, 166), "accent": (149, 165, 166), "text": (220, 220, 220), "rarity_color": (149, 165, 166)}
    }

    pal = colors.get(rarity, colors["обычный"])

    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)

    font_title = load_font(22)
    font_name = load_font(36)
    font_book = load_font(20)
    font_author = load_font(18)
    font_rarity = load_font(26)
    font_footer = load_font(14)

    # Рамка
    border_width = 8
    draw.rectangle([(border_width, border_width), (width - border_width, height - border_width)], outline=pal["border"], width=3)

    # Заголовок
    draw.text((width//2, 15), "ЛИТЕРАТУРНЫЙ ГЕРОЙ", fill=pal["accent"], font=font_title, anchor="mt")

    # Обложка
    cover_img = load_cover(hero["book"])
    if cover_img:
        cover_img = cover_img.resize((180, 250), Image.Resampling.LANCZOS)
        x = (width - 180) // 2
        y = 60
        img.paste(cover_img, (x, y), cover_img)
        draw.rectangle([(x-3, y-3), (x+183, y+253)], outline=pal["border"], width=2)
    else:
        draw.text((width//2, 150), "📚", fill=pal["border"], font=load_font(80), anchor="mt")

    # Имя героя
    y_offset = 340
    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
        draw.text((width//2 + dx, y_offset + dy), hero["name"], fill=(0,0,0), font=font_name, anchor="mt")
    draw.text((width//2, y_offset), hero["name"], fill=pal["text"], font=font_name, anchor="mt")

    # Разделитель
    y_offset += 50
    draw.line([(60, y_offset), (width - 60, y_offset)], fill=pal["accent"], width=2)
    y_offset += 30

    # Книга
    draw.text((width//2, y_offset), hero["book"], fill=(200, 200, 200), font=font_book, anchor="mt")
    y_offset += 30

    # Автор
    draw.text((width//2, y_offset), hero["author"], fill=(180, 180, 180), font=font_author, anchor="mt")
    y_offset += 45

    # Редкость
    rarity_labels = {"легендарный": "ЛЕГЕНДАРНЫЙ", "эпический": "ЭПИЧЕСКИЙ", "редкий": "РЕДКИЙ", "обычный": "ОБЫЧНЫЙ"}
    rarity_text = rarity_labels.get(rarity, "ОБЫЧНЫЙ")
    draw.text((width//2, y_offset), rarity_text, fill=pal["rarity_color"], font=font_rarity, anchor="mt")

    # Нижний колонтитул
    draw.text((width//2, height - 20), "Создано с любовью к литературе", fill=(80, 80, 80), font=font_footer, anchor="mt")

    bio = io.BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio