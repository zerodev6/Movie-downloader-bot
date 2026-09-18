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
        
        # Regroup handlers so text handlers don't override callback handlers or vice versa
        disp = self.dispatcher
        if 0 in disp.groups:
            all_handlers = list(disp.groups[0])
            for i, handler in enumerate(all_handlers):
                disp.remove_handler(handler, group=0)
                disp.add_handler(handler, group=i+1)

        await self.set_bot_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("help", "How to use the bot"),
            BotCommand("about", "About the bot"),
            BotCommand("info", "Check your account info")
        ])
        logging.info("Bot Started and Commands Set!")

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
