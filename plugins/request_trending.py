from pyrogram import Client, filters
from database import files_col, db
from config import OWNER_ID, LOG_CHANNEL

@Client.on_message(filters.command("request") & (filters.group | filters.private))
async def request_movie(client, message):
    if len(message.command) < 2:
        return await message.reply("⚠️ Please provide a movie name.\nFormat: `/request Movie Name`")
    movie = message.text.split(" ", 1)[1]
    
    # Notify admins/LOG_CHANNEL
    req_text = f"**🎬 New Movie Request**\n\n**User:** {message.from_user.mention} (`{message.from_user.id}`)\n**Movie:** `{movie}`"
    try:
        await client.send_message(LOG_CHANNEL, req_text)
        await message.reply(f"✅ Your request for `{movie}` has been sent to the admins!")
    except Exception as e:
        await message.reply("❌ Failed to send request.")

@Client.on_message(filters.command("trending") & (filters.group | filters.private))
async def trending_movies(client, message):
    # Fetch top 10 movies by clicks
    cursor = files_col.find({"clicks": {"$exists": True}}).sort("clicks", -1).limit(10)
    top_movies = await cursor.to_list(length=10)
    
    if not top_movies:
        return await message.reply("No trending movies yet!")
        
    text = "🔥 **Top 10 Trending Movies This Week** 🔥\n\n"
    for idx, m in enumerate(top_movies):
        text += f"**{idx+1}.** `{m['file_name']}` ({m.get('clicks', 0)} downloads)\n"
        
    await message.reply(text)
