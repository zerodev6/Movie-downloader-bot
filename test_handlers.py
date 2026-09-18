from pyrogram import Client
from pyrogram.handlers import MessageHandler

app = Client("test", api_id=1, api_hash="1")
@app.on_message()
async def test(client, message): pass

print(app.dispatcher.groups)
