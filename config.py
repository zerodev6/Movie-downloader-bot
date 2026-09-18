import os
import sys
import logging

try:
    API_ID = int(os.environ.get("API_ID", "123456"))
except ValueError:
    logging.error("CRITICAL ERROR: API_ID must be a number! It looks like you pasted your API_HASH into the API_ID field.")
    sys.exit(1)

API_HASH = os.environ.get("API_HASH", "your_api_hash")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_bot_token")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "movie_bot_db")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1001234567890"))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1001234567891"))
PREMIUM_LOGS = int(os.environ.get("PREMIUM_LOGS", "-1001234567892"))
FORCE_SUB_CHANNELS = os.environ.get("FORCE_SUB_CHANNELS", "-1001234567893,-1001234567894")
OWNER_ID = int(os.environ.get("OWNER_ID", "123456789"))
DEV_NAME = os.environ.get("DEV_NAME", "Spidey2189")
DEV_LINK = os.environ.get("DEV_LINK", "https://t.me/Spidey2189")
WORKERS = int(os.environ.get("WORKERS", "500"))
PORT = int(os.environ.get("PORT", "8080"))
CACHE_TIME = int(os.environ.get("CACHE_TIME", "300"))
FILE_AUTO_DEL_TIMER = int(os.environ.get("FILE_AUTO_DEL_TIMER", "600"))
