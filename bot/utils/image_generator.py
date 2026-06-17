import io
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PORTRAITS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'portraits')

try:
    FONT_LARGE = ImageFont.truetype("arial.ttf", 40)
    FONT_MEDIUM = ImageFont.truetype("arial.ttf", 26)
    FONT_SMALL = ImageFont.truetype("arial.ttf", 20)
except:
    FONT_LARGE = ImageFont.load_default()
    FONT_MEDIUM = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()

def load_portrait(filename):
    if not filename:
        return None
    path = os.path.join(PORTRAITS_DIR, filename)
    try:
        return Image.open(path).convert("RGBA")
    except:
        return None

def draw_circular_frame(draw, center_x, center_y, radius, color, width=6, dot_count=24):
    """Рисует красивую рамку с точками по кругу."""
    # Основной круг
    draw.ellipse(
        (center_x - radius, center_y - radius, center_x + radius, center_y + radius),
        outline=color,
        width=width
    )
    # Внутренний круг (более светлый)
    inner_radius = radius - width - 4
    draw.ellipse(
        (center_x - inner_radius, center_y - inner_radius, center_x + inner_radius, center_y + inner_radius),
        outline=(255, 215, 0, 128),
        width=2
    )
    # Точки по кругу
    if dot_count > 0:
        for i in range(dot_count):
            angle = 360 / dot_count * i
            import math
            x = center_x + (radius - 6) * math.cos(math.radians(angle))
            y = center_y + (radius - 6) * math.sin(math.radians(angle))
            draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 215, 0))

def create_hero_card(hero):
    width, height = 600, 800
    rarity = hero.get("rarity", "обычный")

    # Базовый фон
    if rarity == "легендарный":
        # Градиентный фон тёмно-золотой
        img = Image.new('RGB', (width, height), color=(30, 20, 10))
        for i in range(height):
            r = 50 + int((255 - 50) * i / height)
            g = 40 + int((200 - 40) * i / height)
            b = 20 + int((100 - 20) * i / height)
            draw = ImageDraw.Draw(img)
            draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))
    else:
        img = Image.new('RGB', (width, height), color=(20, 20, 40))

    draw = ImageDraw.Draw(img)

    # Рамка карточки
    border_width = 10
    if rarity == "легендарный":
        # Золотая рамка с градиентом
        for i in range(border_width):
            color_val = 255 - i * 15
            if color_val < 150:
                color_val = 150
            draw.rectangle(
                [(i, i), (width - i, height - i)],
                outline=(color_val, 200, 50),
                width=1
            )
    else:
        rarity_colors = {
            "эпический": (255, 215, 0),
            "редкий": (52, 152, 219),
            "обычный": (149, 165, 166)
        }
        color = rarity_colors.get(rarity, (100, 100, 100))
        draw.rectangle(
            [(border_width, border_width), (width - border_width, height - border_width)],
            outline=color,
            width=border_width
        )

    # Портрет для легендарных
    portrait = None
    if rarity == "легендарный" and "portrait" in hero:
        portrait = load_portrait(hero["portrait"])

    # Центрируем портрет
    if portrait:
        # Масштабируем до 250x250
        portrait = portrait.resize((250, 250), Image.Resampling.LANCZOS)
        # Круглая маска
        mask = Image.new('L', (250, 250), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 250, 250), fill=255)
        portrait.putalpha(mask)
        # Смещение вверх
        x = (width - 250) // 2
        y = 120  # отступ сверху
        img.paste(portrait, (x, y), portrait)
        # Рисуем красивую рамку вокруг портрета
        center_x = width // 2
        center_y = y + 125
        draw_circular_frame(draw, center_x, center_y, 130, (255, 215, 0), width=8, dot_count=24)
        # Добавляем сияние (полупрозрачные лучи)
        for i in range(8):
            angle = 45 * i
            import math
            x1 = center_x + 140 * math.cos(math.radians(angle))
            y1 = center_y + 140 * math.sin(math.radians(angle))
            x2 = center_x + 170 * math.cos(math.radians(angle))
            y2 = center_y + 170 * math.sin(math.radians(angle))
            draw.line([(x1, y1), (x2, y2)], fill=(255, 215, 0, 100), width=4)
    else:
        # Если портрета нет — иконка книги
        y = 180
        draw.text((width//2, y), "📜", fill=(200, 200, 200), font=FONT_LARGE, anchor="mt")

    # Имя героя
    y_offset = 420 if portrait else 80
    draw.text((width//2, y_offset), hero["name"], fill=(255, 255, 255), font=FONT_LARGE, anchor="mt")

    # Разделитель
    y_offset += 50
    draw.line([(80, y_offset), (width - 80, y_offset)], fill=(100, 100, 100), width=2)
    y_offset += 30

    # Книга
    draw.text((width//2, y_offset), f"📖 {hero['book']}", fill=(200, 200, 200), font=FONT_MEDIUM, anchor="mt")
    y_offset += 45

    # Автор
    draw.text((width//2, y_offset), f"✍️ {hero['author']}", fill=(150, 150, 150), font=FONT_SMALL, anchor="mt")
    y_offset += 60

    # Редкость
    rarity_emoji_map = {
        "легендарный": "⭐ ЛЕГЕНДАРНЫЙ",
        "эпический": "⭐ ЭПИЧЕСКИЙ",
        "редкий": "🔵 РЕДКИЙ",
        "обычный": "📘 ОБЫЧНЫЙ"
    }
    rarity_text = rarity_emoji_map.get(rarity, "ОБЫЧНЫЙ")
    color = (255, 215, 0) if rarity == "легендарный" else (200, 200, 200)
    draw.text((width//2, y_offset), rarity_text, fill=color, font=FONT_MEDIUM, anchor="mt")

    # Подпись внизу
    draw.text((width//2, height - 40), "🎴 Литературный Герой", fill=(80, 80, 80), font=FONT_SMALL, anchor="mt")

    # Сохраняем
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio
           