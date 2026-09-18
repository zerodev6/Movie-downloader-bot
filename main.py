from pyrogram import Client
from pyrogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiohttp import web
from config import API_ID, API_HASH, BOT_TOKEN, PORT, WORKERS, LOG_CHANNEL, DB_CHANNEL, OWNER_ID
import logging
import asyncio
from database import users_col, files_col

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
        
        user_commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "How to use the bot"),
            BotCommand("about", "About the bot"),
            BotCommand("info", "Check your account info"),
            BotCommand("trending", "Top 10 Trending Movies"),
            BotCommand("request", "Request a movie")
        ]
        
        admin_commands = user_commands + [
            BotCommand("stats", "Check bot statistics"),
            BotCommand("broadcast", "Broadcast a message"),
            BotCommand("deleteall", "Delete all indexed files")
        ]
        
        try:
            await self.set_bot_commands(user_commands, scope=BotCommandScopeDefault())
            await self.set_bot_commands(admin_commands, scope=BotCommandScopeChat(chat_id=OWNER_ID))
            logging.info("Bot Started and Scoped Commands Set!")
        except Exception as e:
            logging.warning(f"Could not set scoped commands: {e}")
            logging.info("Bot Started!")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped!")

bot_instance = Bot()

async def dashboard(request):
    import state
    
    total_users = await users_col.count_documents({})
    total_movies = await files_col.count_documents({})
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bot Dashboard</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f4f4f5; padding: 2rem; display: flex; justify-content: center; align-items: flex-start; height: 100vh; margin: 0; box-sizing: border-box; }}
            .container {{ width: 100%; max-width: 600px; display: flex; flex-direction: column; gap: 1.5rem; }}
            .card {{ background: white; padding: 2rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }}
            h1 {{ margin-top: 0; color: #18181b; font-size: 1.5rem; }}
            h2 {{ margin-top: 0; color: #3f3f46; font-size: 1.25rem; }}
            .status-indicator {{ display: inline-flex; align-items: center; justify-content: center; width: 100%; gap: 0.5rem; padding: 0.75rem 1rem; border-radius: 0.5rem; font-weight: 500; cursor: pointer; transition: all 0.2s; border: none; font-size: 1rem; }}
            .status-active {{ background: #dcfce7; color: #166534; }}
            .status-maintenance {{ background: #fee2e2; color: #991b1b; }}
            .dot {{ width: 8px; height: 8px; border-radius: 50%; }}
            .dot-active {{ background: #22c55e; }}
            .dot-maintenance {{ background: #ef4444; }}
            
            .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1.5rem; }}
            .stat-box {{ background: #f8fafc; padding: 1.5rem; border-radius: 0.5rem; text-align: center; border: 1px solid #e2e8f0; }}
            .stat-value {{ font-size: 2rem; font-weight: 700; color: #0f172a; line-height: 1; }}
            .stat-label {{ color: #64748b; font-size: 0.875rem; margin-top: 0.5rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }}
            
            textarea {{ width: 100%; padding: 0.75rem; border: 1px solid #d4d4d8; border-radius: 0.5rem; resize: vertical; min-height: 100px; font-family: inherit; margin-bottom: 1rem; box-sizing: border-box; }}
            .btn-broadcast {{ background: #3b82f6; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 0.5rem; font-weight: 500; cursor: pointer; width: 100%; transition: background 0.2s; }}
            .btn-broadcast:hover {{ background: #2563eb; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card" style="text-align: center;">
                <h1>Bot Control Panel</h1>
                <p style="color: #71717a; margin-bottom: 1.5rem;">Click the status badge to toggle maintenance mode.</p>
                <button id="statusBtn" class="status-indicator {'status-maintenance' if state.is_maintenance else 'status-active'}" onclick="toggleStatus()">
                    <div id="statusDot" class="dot {'dot-maintenance' if state.is_maintenance else 'dot-active'}"></div>
                    <span id="statusText">{'Maintenance Mode' if state.is_maintenance else 'Bot Active'}</span>
                </button>
            </div>
            
            <div class="card">
                <h2>Live Statistics</h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-value">{total_users}</div>
                        <div class="stat-label">Total Users</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{total_movies}</div>
                        <div class="stat-label">Indexed Movies</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Web Broadcaster</h2>
                <textarea id="broadcastMsg" placeholder="Type an announcement to send to all users..."></textarea>
                <button class="btn-broadcast" onclick="sendBroadcast()" id="bcastBtn">Send Broadcast</button>
            </div>
        </div>

        <script>
            async function toggleStatus() {{
                const btn = document.getElementById('statusBtn');
                btn.disabled = true;
                btn.style.opacity = '0.7';
                try {{
                    const response = await fetch('/api/maintenance', {{ method: 'POST' }});
                    const data = await response.json();
                    const dot = document.getElementById('statusDot');
                    const text = document.getElementById('statusText');
                    if (data.is_maintenance) {{
                        btn.className = 'status-indicator status-maintenance';
                        dot.className = 'dot dot-maintenance';
                        text.innerText = 'Maintenance Mode';
                    }} else {{
                        btn.className = 'status-indicator status-active';
                        dot.className = 'dot dot-active';
                        text.innerText = 'Bot Active';
                    }}
                }} catch (e) {{ alert('Failed to update status'); }} finally {{
                    btn.disabled = false;
                    btn.style.opacity = '1';
                }}
            }}
            
            async function sendBroadcast() {{
                const msg = document.getElementById('broadcastMsg').value.trim();
                if (!msg) return alert('Message cannot be empty!');
                
                const btn = document.getElementById('bcastBtn');
                btn.disabled = true;
                btn.innerText = 'Broadcasting...';
                
                try {{
                    const res = await fetch('/api/broadcast', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{message: msg}})
                    }});
                    const data = await res.json();
                    alert(data.success ? 'Broadcast completed successfully!' : 'Failed to broadcast.');
                    if(data.success) document.getElementById('broadcastMsg').value = '';
                }} catch (e) {{ alert('Error sending broadcast'); }} finally {{
                    btn.disabled = false;
                    btn.innerText = 'Send Broadcast';
                }}
            }}
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def toggle_maintenance(request):
    import state
    state.is_maintenance = not state.is_maintenance
    logging.info(f"Maintenance mode toggled: {state.is_maintenance}")
    return web.json_response({"is_maintenance": state.is_maintenance})

async def web_broadcast(request):
    try:
        data = await request.json()
        msg = data.get('message', '')
        if not msg:
            return web.json_response({"success": False, "error": "No message"})
            
        cursor = users_col.find({})
        users = await cursor.to_list(length=None)
        
        # Simple background broadcast (for production, use task queues)
        async def do_broadcast():
            sent = 0
            for u in users:
                try:
                    await bot_instance.send_message(u['id'], f"📢 **Announcement**\n\n{msg}")
                    sent += 1
                    await asyncio.sleep(0.1) # Flood wait protection
                except Exception:
                    pass
            logging.info(f"Web broadcast sent to {sent} users.")
            
        asyncio.create_task(do_broadcast())
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

async def start_webserver():
    app = web.Application()
    app.router.add_get('/', dashboard)
    app.router.add_post('/api/maintenance', toggle_maintenance)
    app.router.add_post('/api/broadcast', web_broadcast)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logging.info(f"Web server started on port {PORT}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_webserver())
    bot_instance.run()
