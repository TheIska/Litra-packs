import io
import os
from PIL import Image, ImageDraw, ImageFont

# Пути
PORTRAITS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'portraits')
FONTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')

def load_font(size, filename="arial.ttf"):
    """Загружает шрифт с поддержкой кириллицы"""
    try:
        # Сначала ищем в папке проекта
        font_path = os.path.join(FONTS_DIR, filename)
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        # Если нет, пробуем системные шрифты (для Linux)
        system_fonts = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 
                       "/usr/share/fonts/dejavu/DejaVuSans.ttf",
                       "/System/Library/Fonts/Helvetica.ttc"]
        for path in system_fonts:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        # Если ничего не найдено, используем стандартный (но без кириллицы)
        return ImageFont.load_default()
    except:
        return ImageFont.load_default()

def load_portrait(filename):
    if not filename:
        return None
    path = os.path.join(PORTRAITS_DIR, filename)
    try:
        return Image.open(path).convert("RGBA")
    except:
        return None

def create_hero_card(hero):
    width, height = 600, 800
    rarity = hero.get("rarity", "обычный")

    # Цвета для разных редкостей
    colors = {
        "легендарный": {
            "bg_start": (60, 40, 20),
            "bg_end": (30, 20, 10),
            "border": (255, 215, 0),
            "accent": (255, 215, 0),
            "text": (255, 255, 255),
            "rarity_color": (255, 215, 0)
        },
        "эпический": {
            "bg_start": (40, 10, 60),
            "bg_end": (20, 5, 30),
            "border": (155, 89, 182),
            "accent": (155, 89, 182),
            "text": (255, 255, 255),
            "rarity_color": (155, 89, 182)
        },
        "редкий": {
            "bg_start": (10, 30, 60),
            "bg_end": (5, 15, 40),
            "border": (52, 152, 219),
            "accent": (52, 152, 219),
            "text": (255, 255, 255),
            "rarity_color": (52, 152, 219)
        },
        "обычный": {
            "bg_start": (40, 40, 40),
            "bg_end": (20, 20, 20),
            "border": (149, 165, 166),
            "accent": (149, 165, 166),
            "text": (220, 220, 220),
            "rarity_color": (149, 165, 166)
        }
    }

    pal = colors.get(rarity, colors["обычный"])

    # Градиентный фон
    img = Image.new('RGB', (width, height))
    for y in range(height):
        ratio = y / height
        r = int(pal["bg_start"][0] * (1 - ratio) + pal["bg_end"][0] * ratio)
        g = int(pal["bg_start"][1] * (1 - ratio) + pal["bg_end"][1] * ratio)
        b = int(pal["bg_start"][2] * (1 - ratio) + pal["bg_end"][2] * ratio)
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))

    draw = ImageDraw.Draw(img)

    # Шрифты (загружаем с поддержкой кириллицы)
    font_title = load_font(30)
    font_icon = load_font(100)
    font_name = load_font(48)   # Увеличен размер
    font_book = load_font(32)   # Увеличен размер
    font_author = load_font(28) # Увеличен размер
    font_rarity = load_font(36) # Увеличен размер
    font_footer = load_font(18)

    # Рамка
    border_width = 10
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=pal["border"],
        width=4
    )
    inner_offset = border_width + 8
    draw.rectangle(
        [(inner_offset, inner_offset), (width - inner_offset, height - inner_offset)],
        outline=pal["border"],
        width=2
    )

    # Заголовок
    draw.text((width//2, 20), "📖 ЛИТЕРАТУРНЫЙ ГЕРОЙ", fill=pal["accent"], font=font_title, anchor="mt")

    # Портрет (только для легендарных)
    portrait = None
    if rarity == "легендарный" and "portrait" in hero:
        portrait = load_portrait(hero["portrait"])

    if portrait:
        portrait = portrait.resize((220, 220), Image.Resampling.LANCZOS)
        mask = Image.new('L', (220, 220), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 220, 220), fill=255)
        portrait.putalpha(mask)
        x = (width - 220) // 2
        y = 80
        img.paste(portrait, (x, y), portrait)
        draw.ellipse((x-8, y-8, x+228, y+228), outline=pal["border"], width=6)
    else:
        draw.text((width//2, 140), "📜", fill=pal["border"], font=font_icon, anchor="mt")

    # Имя героя
    y_offset = 380 if portrait else 280
    # Тень
    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
        draw.text((width//2 + dx, y_offset + dy), hero["name"], fill=(0,0,0), font=font_name, anchor="mt")
    draw.text((width//2, y_offset), hero["name"], fill=pal["text"], font=font_name, anchor="mt")

    # Разделитель
    y_offset += 60
    draw.line([(80, y_offset), (width - 80, y_offset)], fill=pal["accent"], width=2)
    y_offset += 35

    # Книга
    draw.text((width//2, y_offset), f"📖 {hero['book']}", fill=(200, 200, 200), font=font_book, anchor="mt")
    y_offset += 45

    # Автор
    draw.text((width//2, y_offset), f"✍️ {hero['author']}", fill=(180, 180, 180), font=font_author, anchor="mt")
    y_offset += 65

    # Редкость
    rarity_emoji_map = {
        "легендарный": "👑",
        "эпический": "⭐",
        "редкий": "🔵",
        "обычный": "📘"
    }
    rarity_labels = {
        "легендарный": "ЛЕГЕНДАРНЫЙ",
        "эпический": "ЭПИЧЕСКИЙ",
        "редкий": "РЕДКИЙ",
        "обычный": "ОБЫЧНЫЙ"
    }
    emoji = rarity_emoji_map.get(rarity, "📘")
    label = rarity_labels.get(rarity, "ОБЫЧНЫЙ")
    rarity_text = f"{emoji} {label}"
    # Тень
    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2)]:
        draw.text((width//2 + dx, y_offset + dy), rarity_text, fill=(0,0,0), font=font_rarity, anchor="mt")
    draw.text((width//2, y_offset), rarity_text, fill=pal["rarity_color"], font=font_rarity, anchor="mt")

    # Колонтитул
    draw.text((width//2, height - 30), "🎴 Создано с любовью к литературе", fill=(100, 100, 100), font=font_footer, anchor="mt")

    # Сохраняем
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio