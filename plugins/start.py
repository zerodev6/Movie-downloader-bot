import random
import string
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import add_user, users_col, is_premium
from utils import force_sub
from config import DEV_LINK

START_TXT = """<b>ʜᴇʏ, {name}!</b> 🚀

ɪ'ᴍ ᴀ ᴘᴏᴡᴇʀғᴜʟ <b>ᴍᴏᴠɪᴇ & ᴛᴠ sᴇʀɪᴇs sᴇᴀʀᴄʜ ʙᴏᴛ</b> 🤖
ɪ ᴄᴀɴ ғɪɴᴅ ᴀɴʏ ᴍᴏᴠɪᴇ ᴏʀ sᴇʀɪᴇs ʏᴏᴜ ᴡᴀɴᴛ ⚡
ᴊᴜsᴛ sᴇɴᴅ ᴍᴇ ᴛʜᴇ ɴᴀᴍᴇ ᴏғ ᴛʜᴇ ᴍᴏᴠɪᴇ ᴏʀ ᴛᴠ sᴇʀɪᴇs 🔗"""

HELP_TXT = """<b>✨ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴍᴏᴠɪᴇ ʙᴏᴛ ✨</b>

1️⃣ <b>sᴇɴᴅ ᴀ ɴᴀᴍᴇ:</b> sᴇɴᴅ ᴀɴʏ ᴍᴏᴠɪᴇ ᴏʀ sᴇʀɪᴇs ɴᴀᴍᴇ 🎬
2️⃣ <b>sᴇᴀʀᴄʜ:</b> ɪ ᴡɪʟʟ sᴇᴀʀᴄʜ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ 🔍
3️⃣ <b>ɢᴇᴛ ᴍᴏᴠɪᴇ:</b> ɢᴇᴛ ʏᴏᴜʀ ᴍᴏᴠɪᴇ ᴡɪᴛʜ ᴅᴏᴡɴʟᴏᴀᴅ/ᴡᴀᴛᴄʜ ᴏɴʟɪɴᴇ ʟɪɴᴋs 🚀"""

ABOUT_TXT = """╭────[ ᴍʏ ᴅᴇᴛᴀɪʟs ]────⍟
├⍟ Mʏ Nᴀᴍᴇ : {bot_name}
├⍟ Dᴇᴠᴇʟᴏᴘᴇʀ : <a href='{dev_link}'>Spidey2189</a> 👨💻
├⍟ Lɪʙʀᴀʀʏ : <a href='https://github.com/pyrogram/pyrogram'>ᴘʏʀᴏɢʀᴀᴍ</a> 📚
├⍟ Lᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/'>ᴘʏᴛʜᴏɴ 𝟹</a> 🐍
├⍟ Dᴀᴛᴀʙᴀsᴇ : <a href='https://www.mongodb.com/'>ᴍᴏɴɢᴏ ᴅʙ</a> 🍃
├⍟ Bᴜɪʟᴅ Sᴛᴀᴛᴜs : ᴠ𝟸.𝟶 [ ᴜʟᴛʀᴀ ] 🚀
╰───────────────⍟"""

PICS_URL = ["https://api.aniwallpaper.workers.dev/random?type=girl"]

def get_random_mix_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

@Client.on_message(filters.command("start") & filters.private)
@force_sub
async def start_cmd(client, message):
    await add_user(message.from_user.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username, message.from_user.dc_id)
    
    # 1. Send Sticker
    sticker_msg = await message.reply_sticker("CAACAgIAAxkBAAEQZtFpgEdROhGouBVFD3e0K-YjmVHwsgACtCMAAphLKUjeub7NKlvk2TgE")
    
    # 2. Auto Delete Sticker
    await asyncio.sleep(2)
    await sticker_msg.delete()
    
    # 3. Welcome Image
    welcome_image = f"{random.choice(PICS_URL)}?r={get_random_mix_id()}"
    
    # 4 & 5. Welcome Text & Buttons
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Search Movie", switch_inline_query="")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help"), InlineKeyboardButton("📊 Info", callback_data="about")]
    ])
    
    await message.reply_photo(
        photo=welcome_image,
        caption=START_TXT.format(name=message.from_user.first_name),
        reply_markup=buttons
    )

@Client.on_message(filters.command("info") & filters.private)
async def info_cmd(client, message):
    user_id = message.from_user.id
    user_data = await users_col.find_one({"user_id": user_id})
    
    if not user_data:
        await message.reply("User data not found in DB.")
        return
        
    first_name = user_data.get("first_name", "N/A")
    last_name = user_data.get("last_name", "")
    username = user_data.get("username", "N/A")
    dc_id = user_data.get("dc_id", "N/A")
    verified = user_data.get("verified", False)
    status = "Yes ✅" if await is_premium(user_id) else "No ❌"
    
    info_text = f"""➲ First Name: {first_name}
➲ Last Name: {last_name}
➲ Telegram ID: `{user_id}`
➲ Data Centre: {dc_id}
➲ User Name: @{username}
➲ User Link: [Click Here](tg://user?id={user_id})
➲ Premium: {status}
➲ Verified: {verified}
➲ Referrals: 0"""

    try:
        async for photo in client.get_chat_photos(user_id, limit=1):
            await message.reply_photo(photo.file_id, caption=info_text)
            return
    except Exception:
        pass
        
    await message.reply(info_text)

@Client.on_callback_query(filters.regex(r"^(help|about)$"))
async def cb_handler(client, query):
    if query.data == "help":
        await query.message.edit_caption(
            caption=HELP_TXT,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start")]])
        )
    elif query.data == "about":
        await query.message.edit_caption(
            caption=ABOUT_TXT.format(bot_name=client.me.first_name, dev_link=DEV_LINK),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start")]])
        )
    elif query.data == "start":
        await query.message.edit_caption(
            caption=START_TXT.format(name=query.from_user.first_name),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Search Movie", switch_inline_query="")],
                [InlineKeyboardButton("ℹ️ Help", callback_data="help"), InlineKeyboardButton("📊 Info", callback_data="about")]
            ])
        )
