# Telegram Movie & TV Series Auto-Filter Bot

An advanced, scalable, production-ready Pyrogram bot with MongoDB integration.

## Features
- **Auto-Filter Indexer:** Listens to DB_CHANNEL, indexes media, and replies with regex-based search results.
- **Force Subscription:** Enforces channel subscription before allowing users to search.
- **MongoDB Async:** Fully async database operations using `motor` for users, files, premium, logs, etc.
- **File Delivery:** Secure file delivery with customizable auto-delete timers.
- **Web Health Check:** Built-in `aiohttp` web server for keep-alive pings.
- **Premium Subscriptions:** Premium user logic and admin management.
- **Advanced Admin Tools:** Broadcast, Stats, Delete All, etc.

## Setup & Deployment

### 1. Prerequisites
- Python 3.8+
- MongoDB Database (Local or MongoDB Atlas)
- Telegram API ID and Hash (from my.telegram.org)
- Telegram Bot Token (from @BotFather)

### 2. Environment Variables
Copy `.env.example` to `.env` and fill in your details:
```env
API_ID=1234567
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_URL=mongodb://localhost:27017
DATABASE_NAME=movie_bot_db
DB_CHANNEL=-1001234567890
LOG_CHANNEL=-1001234567891
PREMIUM_LOGS=-1001234567892
FORCE_SUB_CHANNELS=-1001234567893,-1001234567894
OWNER_ID=123456789
DEV_NAME=Spidey2189
DEV_LINK=https://t.me/Spidey2189
WORKERS=500
PORT=8080
CACHE_TIME=300
FILE_AUTO_DEL_TIMER=600
```

### 3. Local Deployment
```bash
pip install -r requirements.txt
python main.py
```

### 4. Render Deployment
Render will automatically detect the `render.yaml` file in this repository. Just link your GitHub repository to Render and it will deploy as a Background Worker using Python.

### 5. Docker Deployment
```bash
docker build -t movie-bot .
docker run -d --env-file .env movie-bot
```

### 6. Heroku Deployment
Heroku will use the `Procfile`.
```bash
heroku create my-movie-bot
git push heroku main
heroku scale worker=1
```
