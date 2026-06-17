import io
import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

PORTRAITS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'portraits')
FONTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'static', 'fonts')

def load_font(size):
    """Загружает шрифт с поддержкой кириллицы"""
    try:
        # 1. Локальный файл
        font_path = os.path.join(FONTS_DIR, "arial.ttf")
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
        # 2. Системные шрифты
        system_fonts = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        for path in system_fonts:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        # 3. Загрузка из интернета (Roboto)
        url = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            font_data = BytesIO(response.content)
            return ImageFont.truetype(font_data, size)
        # 4. Если всё не удалось — стандартный шрифт
        return ImageFont.load_default()
    except Exception as e:
        print(f"Ошибка загрузки шрифта: {e}")
        return ImageFont.load_default()

# Остальной код без изменений...