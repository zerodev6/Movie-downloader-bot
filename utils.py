import logging
from datetime import datetime
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import FORCE_SUB_CHANNELS, LOG_CHANNEL
from database import logs_col
from functools import wraps

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()]
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)

async def send_log(client, level, message, user_id=None):
    emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "CRITICAL": "🚨"}.get(level, "ℹ️")
    text = f"{emoji} **{level}**\n\n**Message:** {message}\n**User:** `{user_id or 'System'}`\n**Time:** {datetime.now()}"
    try:
        await client.send_message(LOG_CHANNEL, text)
    except Exception:
        pass
    await logs_col.insert_one({"level": level, "message": message, "user_id": user_id, "timestamp": datetime.now()})

def force_sub(func):
    @wraps(func)
    async def wrapper(client, message):
        user_id = message.from_user.id
        if not FORCE_SUB_CHANNELS:
            return await func(client, message)
        
        buttons = []
        for channel in FORCE_SUB_CHANNELS.split(","):
            channel = channel.strip()
            if not channel: continue
            
            if isinstance(channel, str):
                if channel.startswith("-100"):
                    channel = int(channel)
                elif channel.lstrip('-').isdigit():
                    channel = int(channel)
                
            try:
                chat = await client.get_chat(channel)
                await client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                link = chat.invite_link if chat.invite_link else f"https://t.me/{chat.username}"
                buttons.append([InlineKeyboardButton(f"Join {chat.title}", url=link)])
            except Exception as e:
                logging.warning(f"Force Sub Error for {channel}: {e}")
                
        if buttons:
            buttons.append([InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.me.username}?start=start")])
            await message.reply_photo(
                photo="https://i.ibb.co/pr2H8cwT/img-8312532076.jpg",
                caption="**⚠️ Please join our update channels to use this bot!**\n\nClick the buttons below to join the channels, then click 'Try Again' to continue.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
        return await func(client, message)
    return wrapper
