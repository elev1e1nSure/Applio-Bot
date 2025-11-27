"""
Script to check bot configuration.
Run this to verify your .env settings are correct.
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 50)
print("Bot Configuration Check")
print("=" * 50)

# Check BOT_TOKEN
bot_token = os.getenv("BOT_TOKEN")
if bot_token:
    print(f"✅ BOT_TOKEN: {'*' * 20}...{bot_token[-10:]}")
else:
    print("❌ BOT_TOKEN: NOT SET")

# Check ADMIN_ID
admin_id_str = os.getenv("ADMIN_ID", "").strip()
if admin_id_str:
    try:
        admin_id = int(admin_id_str)
        print(f"✅ ADMIN_ID: {admin_id}")
    except ValueError:
        print(f"❌ ADMIN_ID: Invalid value '{admin_id_str}' (must be integer)")
else:
    print("❌ ADMIN_ID: NOT SET")

# Check DB_FILE
db_file = os.getenv("DB_FILE", "applio_bot.db")
print(f"ℹ️  DB_FILE: {db_file}")

# Check APP_COOLDOWN_SECONDS
cooldown = os.getenv("APP_COOLDOWN_SECONDS", "300")
try:
    cooldown_int = int(cooldown)
    print(f"ℹ️  APP_COOLDOWN_SECONDS: {cooldown_int} seconds ({cooldown_int // 60} minutes)")
except ValueError:
    print(f"⚠️  APP_COOLDOWN_SECONDS: Invalid value '{cooldown}' (using default 300)")

print("=" * 50)
print("\nTo get your Telegram User ID:")
print("1. Open Telegram and search for @userinfobot")
print("2. Start a chat with the bot")
print("3. It will show your user ID")
print("4. Copy that ID to ADMIN_ID in your .env file")
print("=" * 50)

