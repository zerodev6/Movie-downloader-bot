import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from database import files_col
from utils import send_log, force_sub
from config import DB_CHANNEL, LOG_CHANNEL, FILE_AUTO_DEL_TIMER

@Client.on_message(filters.channel & (filters.video | filters.document))
async def file_indexer(client, message):
    if message.chat.id != DB_CHANNEL:
        return
        
    media = message.video or message.document
    if not media:
        return

    file_name = message.caption or getattr(media, 'file_name', f"file_{message.id}")
    file_data = {
        "file_id": media.file_id, 
        "file_name": file_name,
        "file_size": getattr(media, 'file_size', 0), 
        "message_id": message.id,
        "chat_id": message.chat.id, 
        "date": message.date,
        "caption": message.caption.markdown if message.caption else ""
    }
    
    if await files_col.find_one({"file_name": file_name}): 
        return  # Duplicate check
        
    await files_col.insert_one(file_data)
    
    try:
        await client.send_message(LOG_CHANNEL, f"**✅ Indexed:** `{file_name}`")
    except Exception as e:
        print(f"Failed to log to channel: {e}")

@Client.on_message(filters.text & (filters.group | filters.private))
async def auto_filter(client, message):
    query = message.text
    if query.startswith("/"): return
    
    search_msg = await message.reply("🔍 **Searching... Please wait...**")
    
    regex = re.compile(query, re.IGNORECASE)
    cursor = files_col.find({"$or": [{"file_name": regex}, {"caption": regex}]}).sort("date", -1).limit(10)
    results = await cursor.to_list(length=10)
    
    if not results:
        await search_msg.edit(f"**❌ No results found for:** `{query}`\n\n_Please check your spelling and try again._")
        return
        
    buttons = []
    for file in results:
        name = file['file_name'][:40] + "..." if len(file['file_name']) > 40 else file['file_name']
        size = round(file['file_size'] / (1024 * 1024), 2)
        # file_id can be very long. We'll use the MongoDB _id (which is a 24-char hex string) instead of the Telegram file_id to guarantee it fits under 64 bytes.
        obj_id_str = str(file['_id'])
        buttons.append([InlineKeyboardButton(f"📁 {name} ({size} MB)", callback_data=f"getfile_{obj_id_str}")])
        
    if len(results) == 1:
        text = f"**✅ I found 1 result for:** `{query}`"
    else:
        text = f"**✅ I found {len(results)} results for:** `{query}`"
        
    await search_msg.edit(text, reply_markup=InlineKeyboardMarkup(buttons))

from bson.objectid import ObjectId

@Client.on_callback_query(filters.regex(r"^getfile_"))
@force_sub
async def get_file_callback(client, query):
    obj_id = query.data.split("_")[1]
    
    try:
        file = await files_col.find_one({"_id": ObjectId(obj_id)})
    except Exception:
        file = None
        
    if not file:
        await query.answer("File not found!", show_alert=True)
        return
        
    # Auto-Delete after FILE_AUTO_DEL_TIMER
    await query.answer("Sending file...")
    
    try:
        sent_msg = await query.message.reply_video(
            video=file["file_id"],
            caption=file.get("caption", file["file_name"]) + f"\n\n_File will be deleted in {FILE_AUTO_DEL_TIMER//60} mins._"
        )
    except Exception:
        # Fallback for documents
        sent_msg = await query.message.reply_document(
            document=file["file_id"],
            caption=file.get("caption", file["file_name"]) + f"\n\n_File will be deleted in {FILE_AUTO_DEL_TIMER//60} mins._"
        )
    
    await asyncio.sleep(FILE_AUTO_DEL_TIMER)
    try:
        await sent_msg.delete()
    except:
        pass
