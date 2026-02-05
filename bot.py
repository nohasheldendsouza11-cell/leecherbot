import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from qbittorrentapi import Client as QbitClient

import config
import helpers

# --- INIT ---
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
current_cookie = config.DEFAULT_TERABOX_COOKIE

# Connect qBit
try:
    qb = QbitClient(host=config.QBIT_HOST, port=config.QBIT_PORT, username=config.QBIT_USER, password=config.QBIT_PASS)
    qb.auth_log_in()
    print("✅ qBittorrent Connected!")
except:
    print("⚠️ qBittorrent Failed")

# --- COMMANDS ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🤖 **Leech Bot Ready**\nSupported: Magnet, Mega, Terabox, GDrive.")

@dp.message(Command("setcookie"))
async def cmd_setcookie(message: types.Message):
    global current_cookie
    try:
        current_cookie = message.text.split(" ", 1)[1]
        await message.reply("✅ Cookie Updated!")
    except:
        await message.reply("⚠️ Usage: `/setcookie ndus=YOUR_COOKIE`")

# --- MAIN LOGIC ---
@dp.message()
async def process_link(message: types.Message):
    if message.from_user.id != config.ADMIN_ID: return
    url = message.text.strip()
    status = await message.reply("🕵️ **Analyzing...**")

    # 1. TORRENT
    if url.startswith("magnet:") or url.endswith(".torrent"):
        try:
            qb.torrents_add(urls=url)
            await bot.edit_message_text("🧲 **Torrent Added!**", chat_id=message.chat.id, message_id=status.message_id)
            asyncio.create_task(monitor_torrent(message.chat.id, status.message_id))
        except Exception as e:
            await bot.edit_message_text(f"❌ Error: {e}", chat_id=message.chat.id, message_id=status.message_id)

    # 2. MEGA
    elif "mega.nz" in url:
        await bot.edit_message_text("☁️ **Mega Download...**", chat_id=message.chat.id, message_id=status.message_id)
        success, res = await asyncio.to_thread(helpers.download_mega, url)
        if success: await trigger_upload(message, status)
        else: await bot.edit_message_text(f"❌ Mega Failed: {res}", chat_id=message.chat.id, message_id=status.message_id)

    # 3. TERABOX
    elif "terabox" in url or "1024tera" in url:
        await bot.edit_message_text("📦 **Terabox Download...**", chat_id=message.chat.id, message_id=status.message_id)
        success, res = await asyncio.to_thread(helpers.download_terabox, url, current_cookie)
        if success: await trigger_upload(message, status)
        else: await bot.edit_message_text(f"❌ Terabox Failed: {res}", chat_id=message.chat.id, message_id=status.message_id)

    # 4. GDRIVE
    elif "drive.google.com" in url:
        await bot.edit_message_text("🔄 **GDrive Download...**", chat_id=message.chat.id, message_id=status.message_id)
        success, res = await asyncio.to_thread(helpers.download_gdrive, url)
        if success: await trigger_upload(message, status)
        else: await bot.edit_message_text(f"❌ GDrive Failed: {res}", chat_id=message.chat.id, message_id=status.message_id)

    else:
        await bot.edit_message_text("❌ Unknown Link", chat_id=message.chat.id, message_id=status.message_id)

# --- UTILS ---
async def trigger_upload(message, status_msg):
    await bot.edit_message_text("🚀 **Uploading to Cloud...**", chat_id=message.chat.id, message_id=status_msg.message_id)
    success, res = await asyncio.to_thread(helpers.upload_to_cloud, config.DOWNLOAD_PATH)
    if success: await bot.edit_message_text(f"✅ **Done!** Files in `{config.RCLONE_REMOTE}`", chat_id=message.chat.id, message_id=status_msg.message_id)
    else: await bot.edit_message_text(f"⚠️ Upload Error: {res}", chat_id=message.chat.id, message_id=status_msg.message_id)

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
    asyncio.run(dp.start_polling(bot))
