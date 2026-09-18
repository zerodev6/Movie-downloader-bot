from pyrogram import Client, filters
from database import users_col, files_col
from config import OWNER_ID
import psutil

@Client.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    total_users = await users_col.count_documents({})
    total_files = await files_col.count_documents({})
    
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    
    stats_text = f"""**📊 Bot Statistics**

👥 Total Users: `{total_users}`
📁 Total Files: `{total_files}`

🖥 CPU Usage: `{cpu_usage}%`
💾 RAM Usage: `{ram_usage}%`"""

    await message.reply(stats_text)

@Client.on_message(filters.command("broadcast") & filters.user(OWNER_ID) & filters.reply)
async def broadcast_cmd(client, message):
    users = users_col.find({})
    success = 0
    failed = 0
    await message.reply("Broadcast started...")
    
    async for user in users:
        try:
            await message.reply_to_message.copy(user['user_id'])
            success += 1
        except Exception:
            failed += 1
            
    await message.reply(f"**Broadcast Completed!**\n\n✅ Success: {success}\n❌ Failed: {failed}")

@Client.on_message(filters.command("deleteall") & filters.user(OWNER_ID))
async def deleteall_cmd(client, message):
    await files_col.delete_many({})
    await message.reply("All indexed files have been cleared from the database!")
