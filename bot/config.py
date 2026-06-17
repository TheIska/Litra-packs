import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла (если он есть)
load_dotenv()

# Обязательные переменные
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан. Укажите его в .env или в переменных окружения.")

# Необязательные переменные с значениями по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_data.db")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PORT = int(os.getenv("PORT", 8080))

# Режим работы (polling или webhook)
MODE = os.getenv("MODE", "polling")  # или "webhook"

# Webhook URL (если используется webhook)
WEBHOOK_URL = os.getenv("WEBHOOK_URL", None)

# Дополнительные настройки
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Настройки базы данных
# Если используется SQLite, то путь к файлу
DB_PATH = DATABASE_URL.replace("sqlite:///", "") if DATABASE_URL.startswith("sqlite:///") else DATABASE_URL