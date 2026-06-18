import io
from PIL import Image, ImageDraw, ImageFont
import os

def load_font(size):
    """Загружает шрифт из папки static/fonts"""
    try:
        font_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')
        for f in os.listdir(font_dir):
            if f.endswith('.ttf') or f.endswith('.otf'):
                return ImageFont.truetype(os.path.join(font_dir, f), size)
    except:
        pass
    return ImageFont.load_default()

def create_hero_card(hero):
    """Создаёт карточку героя"""
    width, height = 400, 560

    # Цвета
    colors = {
        "легендарный": {"bg": (40, 30, 20), "border": (255, 215, 0), "text": (255, 240, 220)},
        "эпический": {"bg": (30, 20, 40), "border": (155, 89, 182), "text": (255, 240, 220)},
        "редкий": {"bg": (20, 30, 40), "border": (52, 152, 219), "text": (255, 240, 220)},
        "обычный": {"bg": (35, 35, 35), "border": (150, 160, 170), "text": (220, 210, 190)}
    }
    pal = colors.get(hero.get("rarity", "обычный"), colors["обычный"])

    img = Image.new('RGB', (width, height), color=pal["bg"])
    draw = ImageDraw.Draw(img)

    font = load_font(30)

    # Рамка
    draw.rectangle([(5, 5), (width-5, height-5)], outline=pal["border"], width=3)

    # Заголовок
    draw.text((width//2, 15), "ЛИТЕРАТУРНЫЙ ГЕРОЙ", fill=pal["border"], font=font, anchor="mt")

    # Имя героя
    draw.text((width//2, 200), hero["name"], fill=pal["text"], font=font, anchor="mt")

    # Книга
    draw.text((width//2, 250), hero["book"], fill=pal["text"], font=font, anchor="mt")

    # Автор
    draw.text((width//2, 290), hero["author"], fill=pal["text"], font=font, anchor="mt")

    # Редкость
    draw.text((width//2, 340), hero["rarity"].upper(), fill=pal["border"], font=font, anchor="mt")

    # Сохраняем
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    bio.seek(0)
    return bio