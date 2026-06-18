import io
import os
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
        
        if os.path.exists(os.path.join(font_dir, font_file)):
            return ImageFont.truetype(os.path.join(font_dir, font_file), size)
        
        for f in os.listdir(font_dir):
            if f.endswith('.ttf') or f.endswith('.otf'):
                return ImageFont.truetype(os.path.join(font_dir, f), size)
        
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def create_hero_card(hero):
    width, height = 500, 700  # Чуть больше для красоты
    rarity = hero.get("rarity", "обычный")

    # Цвета
    colors = {
        "легендарный": {
            "bg": (35, 25, 15),
            "border": (255, 215, 0),
            "accent": (255, 215, 0),
            "text": (255, 240, 220),
            "rare": (255, 215, 0),
            "sub": (200, 180, 150)
        },
        "эпический": {
            "bg": (25, 15, 35),
            "border": (155, 89, 182),
            "accent": (155, 89, 182),
            "text": (255, 240, 220),
            "rare": (155, 89, 182),
            "sub": (200, 180, 150)
        },
        "редкий": {
            "bg": (15, 25, 35),
            "border": (52, 152, 219),
            "accent": (52, 152, 219),
            "text": (255, 240, 220),
            "rare": (52, 152, 219),
            "sub": (200, 180, 150)
        },
        "обычный": {
            "bg": (30, 30, 30),
            "border": (150, 160, 170),
            "accent": (150, 160, 170),
            "text": (220, 210, 190),
            "rare": (150, 160, 170),
            "sub": (180, 170, 150)
        }
    }

    pal = colors.get(rarity, colors["обычный"])

    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)

    # Шрифты
    font_title = load_font(22, "italic")
    font_name = load_font(40, "bold")      # Древнерусский шрифт — для имени
    font_book = load_font(22, "regular")
    font_author = load_font(20, "italic")
    font_rare = load_font(26, "bold")
    font_footer = load_font(16, "italic")

    # 1. РАМКА
    border = 8
    draw.rectangle(
        [(border, border), (width - border, height - border)],
        outline=pal["border"],
        width=3
    )

    # 2. ВЕРХНИЙ ЗАГОЛОВОК (маленький, в углу)
    draw.text((width//2, 20), "ЛИТЕРАТУРНЫЙ ГЕРОЙ", fill=pal["accent"], font=font_title, anchor="mt")

    # 3. ДЕКОРАТИВНАЯ ЛИНИЯ
    y = 50
    draw.line([(80, y), (width - 80, y)], fill=pal["border"], width=1)

    # 4. ОРНАМЕНТ (простой узор)
    for x in range(100, width - 100, 20):
        draw.line([(x, y - 5), (x + 10, y + 5)], fill=pal["border"], width=1)

    y += 20

    # 5. ИМЯ ГЕРОЯ — ЦЕНТР КАРТОЧКИ (древнерусский шрифт)
    name = hero["name"]
    # Тень
    for dx, dy in [(-3,-3), (-3,3), (3,-3), (3,3)]:
        draw.text((width//2 + dx, height//2 - 40 + dy), name, fill=(0, 0, 0), font=font_name, anchor="mt")
    # Основной текст
    draw.text((width//2, height//2 - 40), name, fill=pal["text"], font=font_name, anchor="mt")

    # 6. ДЕКОРАТИВНЫЙ УЗОР ВОКРУГ ИМЕНИ
    y_center = height//2 - 40
    # Маленькие звёздочки по бокам
    draw.text((width//2 - 150, y_center), "✦", fill=pal["accent"], font=load_font(24, "regular"), anchor="mt")
    draw.text((width//2 + 150, y_center), "✦", fill=pal["accent"], font=load_font(24, "regular"), anchor="mt")

    # 7. РАЗДЕЛИТЕЛЬ
    y = height//2 + 30
    draw.line([(60, y), (width - 60, y)], fill=pal["accent"], width=1)

    # 8. КНИГА И АВТОР
    y += 25
    book = hero["book"]
    draw.text((width//2, y), book, fill=pal["sub"], font=font_book, anchor="mt")
    y += 30
    author = hero["author"]
    draw.text((width//2, y), author, fill=pal["sub"], font=font_author, anchor="mt")

    # 9. РЕДКОСТЬ
    y += 45
    rare_labels = {
        "легендарный": "✦ ЛЕГЕНДАРНЫЙ ✦",
        "эпический": "✦ ЭПИЧЕСКИЙ ✦",
        "редкий": "✦ РЕДКИЙ ✦",
        "обычный": "✦ ОБЫЧНЫЙ ✦"
    }
    rare_text = rare_labels.get(rarity, "✦ ОБЫЧНЫЙ ✦")
    draw.text((width//2, y), rare_text, fill=pal["rare"], font=font_rare, anchor="mt")

    # 10. НИЖНИЙ КОЛОНТИТУЛ
    draw.text((width//2, height - 20), "† С любовью к литературе †", fill=(80, 75, 65), font=font_footer, anchor="mt")

    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=92, optimize=True)
    bio.seek(0)
    return bio