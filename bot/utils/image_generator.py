import io
import os
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

def load_cover(book_name):
    """Загружает обложку книги из интернета через Google Books API"""
    try:
        # Кодируем название для URL
        import urllib.parse
        encoded_name = urllib.parse.quote(book_name)
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{encoded_name}&maxResults=1"
        
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
                            return img
    except Exception as e:
        print(f"Не удалось загрузить обложку: {e}")
    
    return None

def create_hero_card(hero):
    """Создаёт карточку героя с обложкой книги"""
    width, height = 500, 700
    rarity = hero.get("rarity", "обычный")

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
    font_book = load_font(24, "regular")
    font_author = load_font(22, "italic")
    font_rare = load_font(28, "bold")
    font_footer = load_font(18, "italic")

    # 1. РАМКА
    border = 8
    draw.rectangle([(border, border), (width - border, height - border)], outline=pal["border"], width=3)
    draw.rectangle([(border + 12, border + 12), (width - border - 12, height - border - 12)], outline=pal["border"], width=1)

    # 2. ЗАГОЛОВОК
    draw.text((width//2, 22), "LITRA PACKS", fill=pal["accent"], font=font_title, anchor="mt")

    # 3. РАЗДЕЛИТЕЛЬ
    y = 55
    draw.line([(60, y), (width - 60, y)], fill=pal["border"], width=1)
    y += 25

    # 4. ОБЛОЖКА КНИГИ (в центре, над именем)
    cover_img = load_cover(hero["book"])
    if cover_img:
        # Уменьшаем обложку до 130x190
        cover_img = cover_img.resize((130, 190), Image.Resampling.LANCZOS)
        x = (width - 130) // 2
        y_cover = 90
        img.paste(cover_img, (x, y_cover), cover_img)
        # Рамка вокруг обложки
        draw.rectangle([(x-3, y_cover-3), (x+133, y_cover+193)], outline=pal["border"], width=2)
        # Смещаем имя вниз, чтобы не наезжало на обложку
        name_y = 310
    else:
        # Если обложки нет — имя остаётся по центру
        name_y = height // 2 - 50

    # 5. ИМЯ ГЕРОЯ
    name = hero["name"]
    for dx, dy in [(-3,-3), (-3,3), (3,-3), (3,3)]:
        draw.text((width//2 + dx, name_y + dy), name, fill=(0, 0, 0), font=font_name, anchor="mt")
    draw.text((width//2, name_y), name, fill=pal["text"], font=font_name, anchor="mt")

    # 6. РАЗДЕЛИТЕЛЬ
    y = name_y + 50
    draw.line([(60, y), (width - 60, y)], fill=pal["accent"], width=1)
    y += 40

    # 7. КНИГА
    book = hero["book"]
    draw.text((width//2, y), f'"{book}"', fill=pal["sub"], font=font_book, anchor="mt")
    y += 32

    # 8. АВТОР
    author = hero["author"]
    draw.text((width//2, y), author, fill=pal["sub"], font=font_author, anchor="mt")
    y += 50

    # 9. РЕДКОСТЬ
    rare_labels = {
        "легендарный": "ЛЕГЕНДАРНЫЙ",
        "эпический": "ЭПИЧЕСКИЙ",
        "редкий": "РЕДКИЙ",
        "обычный": "ОБЫЧНЫЙ"
    }
    rare_text = rare_labels.get(rarity, "ОБЫЧНЫЙ")
    draw.text((width//2, y), rare_text, fill=pal["rare"], font=font_rare, anchor="mt")

    # 10. НИЖНИЙ КОЛОНТИТУЛ
    draw.text((width//2, height - 22), "С любовью к литературе", fill=(80, 75, 65), font=font_footer, anchor="mt")

    # Сохраняем
    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=92, optimize=True)
    bio.seek(0)
    return bio