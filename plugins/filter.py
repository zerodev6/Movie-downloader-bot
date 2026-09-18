import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import files_col, is_premium
from utils import force_sub
from config import DB_CHANNEL, LOG_CHANNEL, FILE_AUTO_DEL_TIMER
from bson.objectid import ObjectId
import math

RESULTS_PER_PAGE = 5

@Client.on_message(filters.channel & (filters.video | filters.document))
async def file_indexer(client, message):
    if message.chat.id != DB_CHANNEL:
        return
        
    media = message.video or message.document
    if not media:
        return

    file_name = message.caption or getattr(media, 'file_name', f"file_{message.id}")
    
    # Auto Rejection for CamRip, PreDVD, HDTS
    file_name_lower = file_name.lower()
    if any(x in file_name_lower for x in ["camrip", "predvd", "hdts", "hd-ts", "hdcam"]):
        return # Do not index these files

    file_data = {
        "file_id": media.file_id, 
        "file_name": file_name,
        "file_size": getattr(media, 'file_size', 0), 
        "message_id": message.id,
        "chat_id": message.chat.id, 
        "date": message.date,
        "caption": message.caption.markdown if message.caption else "",
        "clicks": 0
    }
    
    if await files_col.find_one({"file_name": file_name}): 
        return  # Duplicate check
        
    await files_col.insert_one(file_data)
    
    try:
        await client.send_message(LOG_CHANNEL, f"**✅ Indexed:** `{file_name}`")
    except Exception as e:
        print(f"Failed to log to channel: {e}")

@Client.on_message(filters.text & (filters.group | filters.private), group=1)
async def auto_filter(client, message):
    import state
    if state.is_maintenance:
        await message.reply("🚧 **Maintenance Mode** 🚧\n\nThe bot is currently undergoing maintenance. Please try again later.")
        return

    query = str(message.text)
    if query.startswith("/"): return
    
    search_msg = await message.reply("🔍 **Searching... Please wait...**")
    
    await search_database(query, search_msg, page=1)

async def search_database(query, message_obj, page=1):
    regex = re.compile(re.escape(query), re.IGNORECASE)
    
    # Calculate skip for pagination
    skip = (page - 1) * RESULTS_PER_PAGE
    
    total_results = await files_col.count_documents({"$or": [{"file_name": regex}, {"caption": regex}]})
    cursor = files_col.find({"$or": [{"file_name": regex}, {"caption": regex}]}).sort("date", -1).skip(skip).limit(RESULTS_PER_PAGE)
    results = await cursor.to_list(length=RESULTS_PER_PAGE)
    
    if total_results == 0:
        await message_obj.edit(f"**❌ No results found for:** `{query}`\n\n_Please check your spelling and try again._")
        return
        
    buttons = []
    for file in results:
        name = file['file_name'][:40] + "..." if len(file['file_name']) > 40 else file['file_name']
        size = round(file['file_size'] / (1024 * 1024), 2)
        obj_id_str = str(file['_id'])
        
        # Quality Filters (Visual)
        quality = ""
        if "2160p" in name.lower() or "4k" in name.lower(): quality = " [4K]"
        elif "1080p" in name.lower(): quality = " [1080p]"
        elif "720p" in name.lower(): quality = " [720p]"
        elif "480p" in name.lower(): quality = " [480p]"
        
        buttons.append([InlineKeyboardButton(f"📁 {name}{quality} ({size} MB)", callback_data=f"getfile_{obj_id_str}")])
        
    # Pagination controls
    nav_buttons = []
    total_pages = math.ceil(total_results / RESULTS_PER_PAGE)
    
    # We will pass query directly but encode it safely in callback
    safe_query = query[:20] # keep it short for callback limit
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"page_{page-1}_{safe_query}"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{page+1}_{safe_query}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    text = f"**✅ I found {total_results} results for:** `{query}`\n\n**Page {page}/{total_pages}**"
    await message_obj.edit(text, reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^page_"))
async def page_callback(client, query):
    data = query.data.split("_")
    page = int(data[1])
    search_query = "_".join(data[2:])
    await search_database(search_query, query.message, page)

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
        
    # Premium-Only Check for 4K files
    file_name_lower = file["file_name"].lower()
    if "4k" in file_name_lower or "2160p" in file_name_lower:
        is_prem = await is_premium(query.from_user.id)
        if not is_prem:
            await query.answer("💎 This is a 4K file! You need Premium to download it. Contact Admin.", show_alert=True)
            return

    # Increment clicks for trending feature
    await files_col.update_one({"_id": ObjectId(obj_id)}, {"$inc": {"clicks": 1}})
        
    await query.answer("Sending file...")
    
    try:
        sent_msg = await query.message.reply_video(
            video=file["file_id"],
            caption=file.get("caption", file["file_name"]) + f"\n\n_File will be deleted in {FILE_AUTO_DEL_TIMER//60} mins._",
            protect_content=True
        )
    except Exception:
        sent_msg = await query.message.reply_document(
            document=file["file_id"],
            caption=file.get("caption", file["file_name"]) + f"\n\n_File will be deleted in {FILE_AUTO_DEL_TIMER//60} mins._",
            protect_content=True
        )
        
    # Schedule Auto-Delete
    await asyncio.sleep(FILE_AUTO_DEL_TIMER)
    try:
        await sent_msg.delete()
    except:
        pass
