from pyrogram import Client
from pyrogram.types import BotCommand
from aiohttp import web
from config import API_ID, API_HASH, BOT_TOKEN, PORT, WORKERS, LOG_CHANNEL, DB_CHANNEL
import logging

logging.basicConfig(level=logging.INFO)

class Bot(Client):
    def __init__(self):
        super().__init__(
            "MovieAutoFilterBot",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="plugins"),
            workers=WORKERS
        )

    async def start(self):
        await super().start()
        await self.set_bot_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("help", "How to use the bot"),
            BotCommand("about", "About the bot"),
            BotCommand("info", "Check your account info")
        ])
        logging.info("Bot Started and Commands Set!")
        
        try:
            await self.send_message(
                LOG_CHANNEL,
                "**🚀 Bot Started Successfully!**\n\n"
                "**How to add movies:**\n"
                f"1. Forward or upload your Video/Document files to your Database Channel (`{DB_CHANNEL}`).\n"
                "2. Make sure the file has a clear filename or caption.\n"
                "3. The bot will automatically index it and make it searchable for your users!"
            )
        except Exception as e:
            logging.warning(f"Could not send startup message to LOG_CHANNEL: {e}")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped!")

async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_webserver():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"Web server started on port {PORT}")

if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_webserver())
    Bot().run()
