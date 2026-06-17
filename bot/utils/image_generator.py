import io
import os
from PIL import Image, ImageDraw, ImageFont

# Путь к портретам
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

    # Базовый фон
    if rarity == "легендарный":
        img = Image.new('RGB', (width, height), color=(40, 30, 20))
    else:
        img = Image.new('RGB', (width, height), color=(20, 20, 40))

    draw = ImageDraw.Draw(img)

    # Цвет рамки
    rarity_colors = {
        "легендарный": (255, 215, 0),
        "эпический": (255, 215, 0),
        "редкий": (52, 152, 219),
        "обычный": (149, 165, 166)
    }
    border_color = rarity_colors.get(rarity, (100, 100, 100))

    # Рамка
    border_width = 8
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=border_color,
        width=border_width
    )

    # Портрет (только для легендарных)
    portrait = None
    if rarity == "легендарный" and "portrait" in hero:
        portrait = load_portrait(hero["portrait"])

    if portrait:
        # Масштабируем до 200x200
        portrait = portrait.resize((200, 200), Image.Resampling.LANCZOS)
        # Круглая маска
        mask = Image.new('L', (200, 200), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, 200, 200), fill=255)
        portrait.putalpha(mask)
        # Центрируем
        x = (width - 200) // 2
        y = 120
        img.paste(portrait, (x, y), portrait)
        # Рамка вокруг портрета
        draw.ellipse((x-5, y-5, x+205, y+205), outline=(255, 215, 0), width=4)
    else:
        # Если портрета нет — показываем иконку
        draw.text((width//2, 200), "📜", fill=(200, 200, 200), font=ImageFont.load_default(), anchor="mt")

    # Шрифты (без загрузки внешних — используем стандартный)
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

    # Имя героя
    y_offset = 420 if portrait else 80
    draw.text((width//2, y_offset), hero["name"], fill=(255, 255, 255), font=font_large, anchor="mt")

    # Разделитель
    y_offset += 50
    draw.line([(80, y_offset), (width - 80, y_offset)], fill=(100, 100, 100), width=2)
    y_offset += 30

    # Книга
    draw.text((width//2, y_offset), f"📖 {hero['book']}", fill=(200, 200, 200), font=font_medium, anchor="mt")
    y_offset += 45

    # Автор
    draw.text((width//2, y_offset), f"✍️ {hero['author']}", fill=(150, 150, 150), font=font_small, anchor="mt")
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
    draw.text((width//2, y_offset), rarity_text, fill=color, font=font_medium, anchor="mt")

    # Нижняя подпись
    draw.text((width//2, height - 40), "🎴 Литературный Герой", fill=(80, 80, 80), font=font_small, anchor="mt")

    # Сохраняем в BytesIO
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio