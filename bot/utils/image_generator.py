import io
import os
from PIL import Image, ImageDraw, ImageFont

PORTRAITS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'portraits')

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

    # Рамка с двойной линией
    border_width = 10
    # Внешняя рамка
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=pal["border"],
        width=4
    )
    # Внутренняя рамка
    inner_offset = border_width + 8
    draw.rectangle(
        [(inner_offset, inner_offset), (width - inner_offset, height - inner_offset)],
        outline=pal["border"],
        width=2
    )

    # Заголовок "Литературный Герой" сверху
    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
    except:
        font_title = ImageFont.load_default()
    draw.text((width//2, 20), "📖 ЛИТЕРАТУРНЫЙ ГЕРОЙ", fill=pal["accent"], font=font_title, anchor="mt")

    # Портрет для легендарных
    portrait = None
    if rarity == "легендарный" and "portrait" in hero:
        portrait = load_portrait(hero["portrait"])

    if portrait:
        # Масштабируем до 220x220
        portrait = portrait.resize((220, 220), Image.Resampling.LANCZOS)
        # Круглая маска
        mask = Image.new('L', (220, 220), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 220, 220), fill=255)
        portrait.putalpha(mask)
        # Центрируем
        x = (width - 220) // 2
        y = 80
        img.paste(portrait, (x, y), portrait)
        # Золотая рамка вокруг портрета
        draw.ellipse((x-8, y-8, x+228, y+228), outline=pal["border"], width=6)
    else:
        # Если портрета нет — показываем большую иконку
        try:
            font_icon = ImageFont.truetype("arial.ttf", 100)
        except:
            font_icon = ImageFont.load_default()
        draw.text((width//2, 140), "📜", fill=pal["border"], font=font_icon, anchor="mt")

    # Имя героя
    try:
        font_name = ImageFont.truetype("arial.ttf", 44)
    except:
        font_name = ImageFont.load_default()
    y_offset = 380 if portrait else 280
    # Обводка имени (тень)
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        draw.text((width//2 + dx, y_offset + dy), hero["name"], fill=(0,0,0), font=font_name, anchor="mt")
    draw.text((width//2, y_offset), hero["name"], fill=pal["text"], font=font_name, anchor="mt")

    # Разделитель
    y_offset += 55
    draw.line([(80, y_offset), (width - 80, y_offset)], fill=pal["accent"], width=2)
    y_offset += 30

    # Книга
    try:
        font_book = ImageFont.truetype("arial.ttf", 26)
    except:
        font_book = ImageFont.load_default()
    draw.text((width//2, y_offset), f"📖 {hero['book']}", fill=(200, 200, 200), font=font_book, anchor="mt")
    y_offset += 40

    # Автор
    try:
        font_author = ImageFont.truetype("arial.ttf", 22)
    except:
        font_author = ImageFont.load_default()
    draw.text((width//2, y_offset), f"✍️ {hero['author']}", fill=(180, 180, 180), font=font_author, anchor="mt")
    y_offset += 55

    # Редкость (большая и цветная)
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
    try:
        font_rarity = ImageFont.truetype("arial.ttf", 30)
    except:
        font_rarity = ImageFont.load_default()
    # Обводка для редкости
    for dx, dy in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        draw.text((width//2 + dx, y_offset + dy), f"{emoji} {label}", fill=(0,0,0), font=font_rarity, anchor="mt")
    draw.text((width//2, y_offset), f"{emoji} {label}", fill=pal["rarity_color"], font=font_rarity, anchor="mt")

    # Нижний колонтитул
    try:
        font_footer = ImageFont.truetype("arial.ttf", 16)
    except:
        font_footer = ImageFont.load_default()
    draw.text((width//2, height - 30), "🎴 Создано с любовью к литературе", fill=(100, 100, 100), font=font_footer, anchor="mt")

    # Сохраняем
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio