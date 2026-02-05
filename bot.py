import asyncio
import os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from qbittorrentapi import Client as QbitClient
import config
import helpers

# --- RENDER KEEPALIVE SERVER ---
app = Flask('')
@app.route('/')
def home(): return "I am alive"
def run_http(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): 
    t = Thread(target=run_http)
    t.start()

# --- BOT INIT ---
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
current_cookie = config.DEFAULT_TERABOX_COOKIE

# Connect qBit
try:
    qb = QbitClient(host=config.QBIT_HOST, port=config.QBIT_PORT, username=config.QBIT_USER, password=config.QBIT_PASS)
    qb.auth_log_in()
except: pass

# --- HANDLERS ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 **Hello {message.from_user.first_name}!**\n\n"
        "**Send me a link:**\n🧲 Magnet\n☁️ Mega\n📦 Terabox\n🔄 GDrive\n\n"
        f"🟢 **Mode:** {'Telegram + Cloud' if config.UPLOAD_TO_TELEGRAM else 'Cloud Only'}"
    )

@dp.message(Command("setcookie"))
async def cmd_setcookie(message: types.Message):
    global current_cookie
    current_cookie = message.text.split(" ", 1)[1]
    await message.reply("✅ Cookie Updated!")

@dp.message()
async def process_link(message: types.Message):
    if message.from_user.id != config.ADMIN_ID: return
    url = message.text.strip()
    status = await message.reply("🕵️ **Analyzing Link...**")
    
    success = False
    
    # 1. TORRENT
    if url.startswith("magnet:") or url.endswith(".torrent"):
        try:
            qb.torrents_add(urls=url)
            await bot.edit_message_text("🧲 **Torrent Added!**", chat_id=message.chat.id, message_id=status.message_id)
            asyncio.create_task(monitor_torrent(message.chat.id, status.message_id))
            return 
        except Exception as e:
            await bot.edit_message_text(f"❌ Error: {e}", chat_id=message.chat.id, message_id=status.message_id)
            return

    # 2. MEGA
    elif "mega.nz" in url:
        await bot.edit_message_text("☁️ **Downloading Mega...**", chat_id=message.chat.id, message_id=status.message_id)
        success, res = await asyncio.to_thread(helpers.download_mega, url)

    # 3. TERABOX
    elif "terabox" in url or "1024tera" in url:
        await bot.edit_message_text("📦 **Downloading Terabox...**", chat_id=message.chat.id, message_id=status.message_id)
        success, res = await asyncio.to_thread(helpers.download_terabox, url, current_cookie)

    # 4. GDRIVE
    elif "drive.google.com" in url:
        await bot.edit_message_text("🔄 **Downloading GDrive...**", chat_id=message.chat.id, message_id=status.message_id)
        success, res = await asyncio.to_thread(helpers.download_gdrive, url)

    else:
        await bot.edit_message_text("❌ Unknown Link", chat_id=message.chat.id, message_id=status.message_id)
        return

    # --- UPLOAD SEQUENCE ---
    if success:
        # A. Upload to Telegram (Visible)
        if config.UPLOAD_TO_TELEGRAM:
            files = [os.path.join(config.DOWNLOAD_PATH, f) for f in os.listdir(config.DOWNLOAD_PATH)]
            for f in files:
                await helpers.send_to_telegram(bot, message.chat.id, f, status)
        
        # B. Move to Cloud
        await bot.edit_message_text("🚀 **Syncing to Cloud...**", chat_id=message.chat.id, message_id=status.message_id)
        await asyncio.to_thread(helpers.upload_to_cloud, config.DOWNLOAD_PATH)
        await bot.edit_message_text("✅ **Task Finished!**", chat_id=message.chat.id, message_id=status.message_id)
    else:
        await bot.edit_message_text(f"❌ Failed: {res}", chat_id=message.chat.id, message_id=status.message_id)

async def monitor_torrent(chat_id, message_id):
    last_text = ""
    while True:
        try:
            torrents = qb.torrents_info(filter="downloading")
            if not torrents: break
            t = torrents[0]
            progress = t.progress * 100
            text = f"📥 **{t.name[:15]}...**\n`[{'█'*int(progress/10)}{'░'*(10-int(progress/10))}]` {progress:.1f}%"
            if text != last_text:
                await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, parse_mode="Markdown")
                last_text = text
            await asyncio.sleep(4)
        except: break

if __name__ == "__main__":
    keep_alive()
    asyncio.run(dp.start_polling(bot))
