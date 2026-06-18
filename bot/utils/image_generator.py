import io
import os
from PIL import Image, ImageDraw, ImageFont

def load_font(size):
    """Загружает шрифт из папки static/fonts"""
    try:
        # Путь к папке со шрифтами
        font_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')
        font_path = os.path.join(font_dir, 'regular.ttf')
        
        # Если шрифт есть — используем его
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        
        # Если нет — пробуем другие шрифты в папке
        if os.path.exists(font_dir):
            for f in os.listdir(font_dir):
                if f.endswith('.ttf') or f.endswith('.otf'):
                    return ImageFont.truetype(os.path.join(font_dir, f), size)
        
        # Если ничего нет — стандартный шрифт
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def create_hero_card(hero):
    """Создаёт красивую карточку героя"""
    width, height = 400, 560
    rarity = hero.get("rarity", "обычный")

    # Цвета
    colors = {
        "легендарный": {
            "bg": (40, 30, 20),
            "border": (255, 215, 0),
            "accent": (255, 215, 0),
            "text": (255, 240, 220),
            "rare": (255, 215, 0),
            "sub": (200, 180, 150)
        },
        "эпический": {
            "bg": (30, 20, 40),
            "border": (155, 89, 182),
            "accent": (155, 89, 182),
            "text": (255, 240, 220),
            "rare": (155, 89, 182),
            "sub": (200, 180, 150)
        },
        "редкий": {
            "bg": (20, 30, 40),
            "border": (52, 152, 219),
            "accent": (52, 152, 219),
            "text": (255, 240, 220),
            "rare": (52, 152, 219),
            "sub": (200, 180, 150)
        },
        "обычный": {
            "bg": (35, 35, 35),
            "border": (150, 160, 170),
            "accent": (150, 160, 170),
            "text": (220, 210, 190),
            "rare": (150, 160, 170),
            "sub": (180, 170, 150)
        }
    }

    pal = colors.get(rarity, colors["обычный"])

    # Фон
    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)

    # Шрифт
    font_title = load_font(20)
    font_name = load_font(28)
    font_text = load_font(18)
    font_rare = load_font(22)
    font_footer = load_font(14)

    # 1. РАМКА
    border = 6
    draw.rectangle(
        [(border, border), (width - border, height - border)],
        outline=pal["border"],
        width=3
    )

    # 2. ЗАГОЛОВОК
    draw.text((width//2, 12), "ЛИТЕРАТУРНЫЙ ГЕРОЙ", fill=pal["accent"], font=font_title, anchor="mt")

    # 3. ИКОНКА КНИГИ (вместо обложки, чтобы не тратить время на загрузку)
    draw.text((width//2, 60), "📖", fill=pal["border"], font=load_font(70), anchor="mt")

    # 4. РАЗДЕЛИТЕЛЬ
    y = 150
    draw.line([(30, y), (width - 30, y)], fill=pal["accent"], width=1)
    y += 20

    # 5. ИМЯ ГЕРОЯ (с тенью)
    name = hero["name"]
    draw.text((width//2 + 2, y + 2), name, fill=(0, 0, 0), font=font_name, anchor="mt")
    draw.text((width//2, y), name, fill=pal["text"], font=font_name, anchor="mt")
    y += 40

    # 6. РАЗДЕЛИТЕЛЬ
    draw.line([(40, y), (width - 40, y)], fill=pal["accent"], width=1)
    y += 20

    # 7. НАЗВАНИЕ КНИГИ
    book = hero["book"]
    draw.text((width//2, y), book, fill=pal["sub"], font=font_text, anchor="mt")
    y += 25

    # 8. АВТОР
    author = hero["author"]
    draw.text((width//2, y), author, fill=pal["sub"], font=font_text, anchor="mt")
    y += 35

    # 9. РЕДКОСТЬ
    rare_labels = {
        "легендарный": "★ ЛЕГЕНДАРНЫЙ ★",
        "эпический": "★ ЭПИЧЕСКИЙ ★",
        "редкий": "★ РЕДКИЙ ★",
        "обычный": "★ ОБЫЧНЫЙ ★"
    }
    rare_text = rare_labels.get(rarity, "★ ОБЫЧНЫЙ ★")
    draw.text((width//2, y), rare_text, fill=pal["rare"], font=font_rare, anchor="mt")

    # 10. НИЖНИЙ КОЛОНТИТУЛ
    draw.text((width//2, height - 15), "Создано с любовью к литературе", fill=(80, 75, 65), font=font_footer, anchor="mt")

    # Сохраняем
    bio = io.BytesIO()
    img.save(bio, format='JPEG', quality=90, optimize=True)
    bio.seek(0)
    return bio