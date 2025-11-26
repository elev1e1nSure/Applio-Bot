import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (если он есть)
load_dotenv()

# ============ Bot Configuration ============
# Токен бота, получаем из BotFather
TOKEN = os.getenv('TOKEN', 'YOUR_TOKEN_HERE')

# ID администратора или список ID.
# Сюда бот будет отправлять уведомления о новых заявках.
# !!! Обязательно замените на реальный ID !!!
ADMIN_ID = int(os.getenv('ADMIN_ID', '123456789')) # Ваш личный Telegram ID

# ============ Database Configuration ============
# По умолчанию используем SQLite
DB_FILE = os.getenv('DB_FILE', 'applio_bot.db')

# Если планируется использовать PostgreSQL/другую СУБД:
# DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DB_FILE}')


# ============ Anti-Spam Configuration ============
# Защита от флуда: минимальный интервал между заявками от одного пользователя (в секундах)
APP_COOLDOWN_SECONDS = int(os.getenv('APP_COOLDOWN_SECONDS', '3600')) # 1 час

# ============ Application Limits ============
# Максимальная длина поля для текстовых ответов
MAX_TEXT_LENGTH = 500