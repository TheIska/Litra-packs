import io
import os
import random
import urllib.request
import json
from PIL import Image, ImageDraw, ImageFont

COVERS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'covers')
FONTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')

def load_font(size):
    """Загружает шрифт из папки fonts с подробными логами"""
    print(f"🔍 Ищем шрифт в: {FONTS_DIR}")
    
    try:
        # Проверяем, существует ли папка
        if not os.path.exists(FONTS_DIR):
            print(f"❌ Папка {FONTS_DIR} не существует!")
            return ImageFont.load_default()
        
        # Проверяем содержимое папки
        files = os.listdir(FONTS_DIR)
        print(f"📂 Содержимое папки fonts: {files}")
        
        # Ищем любой .ttf или .otf файл
        for f in files:
            if f.endswith('.ttf') or f.endswith('.otf'):
                font_path = os.path.join(FONTS_DIR, f)
                print(f"✅ Загружаю шрифт: {font_path}")
                return ImageFont.truetype(font_path, size)
        
        print(f"⚠️ В папке {FONTS_DIR} нет .ttf файлов")
        return ImageFont.load_default()
    except Exception as e:
        print(f"❌ Ошибка загрузки шрифта: {e}")
        return ImageFont.load_default()

def load_cover(book_name):
    """Загружает обложку книги: сначала локально, потом из интернета через Google Books API"""
    print(f"📖 Ищем обложку для: {book_name}")
    clean_name = book_name.replace('"', '').replace('«', '').replace('»', '').replace('?', '').replace('!', '')
    
    # 1. Пробуем локально
    extensions = ['.jpg', '.jpeg', '.png', '.webp']
    for ext in extensions:
        path = os.path.join(COVERS_DIR, f"{clean_name}{ext}")
        if os.path.exists(path):
            try:
                print(f"✅ Обложка найдена локально: {path}")
                return Image.open(path).convert("RGBA")
            except Exception as e:
                print(f"⚠️ Не удалось открыть обложку: {e}")
    
    # 2. Ищем через Google Books API
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{urllib.parse.quote(book_name)}&maxResults=1"
        print(f"🌐 Ищем обложку в интернете: {url}")
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            if 'items' in data and len(data['items']) > 0:
                volume = data['items'][0]['volumeInfo']
                if 'imageLinks' in volume:
                    cover_url = volume['imageLinks'].get('thumbnail')
                    if cover_url:
                        print(f"🖼️ Найдена обложка: {cover_url}")
                        with urllib.request.urlopen(cover_url, timeout=5) as img_response:
                            img_data = img_response.read()
                            img = Image.open(io.BytesIO(img_data)).convert("RGBA")
                            # Сохраняем локально, чтобы не качать каждый раз
                            try:
                                os.makedirs(COVERS_DIR, exist_ok=True)
                                local_path = os.path.join(COVERS_DIR, f"{clean_name}.jpg")
                                img.save(local_path, 'JPEG')
                                print(f"💾 Обложка сохранена локально: {local_path}")
                            except:
                                pass
                            return img
    except Exception as e:
        print(f"❌ Не удалось загрузить обложку для {book_name}: {e}")
    
    print(f"⚠️ Обложка не найдена для {book_name}")
    return None

def create_hero_card(hero):
    print(f"🃏 Создаю карточку для: {hero['name']}")
    width, height = 500, 700
    rarity = hero.get("rarity", "обычный")

    # Цвета для разных редкостей
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

    # Создаём фон
    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)

    # Текстура старой бумаги
    for i in range(0, height, 3):
        for j in range(0, width, 3):
            noise = random.randint(-8, 8)
            r = max(0, min(255, pal["bg"][0] + noise))
            g = max(0, min(255, pal["bg"][1] + noise))
            b = max(0, min(255, pal["bg"][2] + noise))
            draw.point((j, i), fill=(r, g, b))

    # Загружаем шрифт
    font = load_font(28)
    print(f"📝 Шрифт загружен: {type(font)}")

    # Рамка
    border_width = 8
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=pal["border"],
        width=3
    )

    # Заголовок
    draw.text((width//2, 15), "ЛИТЕРАТУРНЫЙ ГЕРОЙ", fill=pal["accent"], font=font, anchor="mt")

    # Обложка
    cover_img = load_cover(hero["book"])
    if cover_img:
        cover_img = cover_img.resize((180, 250), Image.Resampling.LANCZOS)
        x = (width - 180) // 2
        y = 55
        img.paste(cover_img, (x, y), cover_img)
        draw.rectangle([(x-3, y-3), (x+183, y+253)], outline=pal["border"], width=2)
    else:
        draw.text((width//2, 150), "📚", fill=pal["border"], font=font, anchor="mt")

    # Имя героя
    y_offset = 340
    draw.text((width//2 + 2, y_offset + 2), hero["name"], fill=(0,0,0), font=font, anchor="mt")
    draw.text((width//2, y_offset), hero["name"], fill=pal["text"], font=font, anchor="mt")

    # Разделитель
    y_offset += 50
    draw.line([(60, y_offset), (width - 60, y_offset)], fill=pal["accent"], width=2)
    y_offset += 30

    # Книга
    draw.text((width//2, y_offset), hero["book"], fill=pal["subtext"], font=font, anchor="mt")
    y_offset += 30

    # Автор
    draw.text((width//2, y_offset), hero["author"], fill=pal["subtext"], font=font, anchor="mt")
    y_offset += 45

    # Редкость
    rarity_labels = {
        "легендарный": "ЛЕГЕНДАРНЫЙ",
        "эпический": "ЭПИЧЕСКИЙ",
        "редкий": "РЕДКИЙ",
        "обычный": "ОБЫЧНЫЙ"
    }
    rarity_text = rarity_labels.get(rarity, "ОБЫЧНЫЙ")
    draw.text((width//2, y_offset), rarity_text, fill=pal["rarity_color"], font=font, anchor="mt")

    # Нижний колонтитул
    draw.text((width//2, height - 20), "Создано с любовью к литературе", fill=(80, 75, 65), font=font, anchor="mt")

    # Сохраняем
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    print(f"✅ Карточка создана для {hero['name']}")
    return bio