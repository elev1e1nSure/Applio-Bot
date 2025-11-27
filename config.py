"""
Configuration module for the Telegram bot.
Reads settings from environment variables.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID_STR = os.getenv("ADMIN_ID", "").strip()

# Database settings
DB_FILE = os.getenv("DB_FILE", "applio_bot.db")

# Anti-spam settings
APP_COOLDOWN_SECONDS = int(os.getenv("APP_COOLDOWN_SECONDS", 300))  # 5 minutes default

# Validate required settings
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in .env file")

if not ADMIN_ID_STR:
    raise ValueError("ADMIN_ID is not set in .env file")

try:
    ADMIN_ID = int(ADMIN_ID_STR)
    if ADMIN_ID <= 0:
        raise ValueError("ADMIN_ID must be a positive integer")
except ValueError as e:
    raise ValueError(f"ADMIN_ID must be a valid integer. Got: {ADMIN_ID_STR}") from e

