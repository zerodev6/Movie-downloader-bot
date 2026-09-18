from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URL, DATABASE_NAME

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

users_col = db['users']
files_col = db['files']
premium_col = db['premium']
logs_col = db['logs']
groups_col = db['groups']
refer_col = db['refer']

async def add_user(user_id, first_name, last_name, username, dc_id):
    if not await users_col.find_one({"user_id": user_id}):
        await users_col.insert_one({
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
            "join_date": None,
            "is_premium": False,
            "search_count": 0,
            "last_search": None,
            "dc_id": dc_id,
            "verified": False
        })

async def is_premium(user_id):
    user = await users_col.find_one({"user_id": user_id})
    return user.get("is_premium", False) if user else False

async def log_activity(level, message, user_id=None, source="bot"):
    from datetime import datetime
    await logs_col.insert_one({
        "level": level,
        "message": message,
        "source": source,
        "user_id": user_id,
        "timestamp": datetime.now()
    })
