import os
import asyncio
import subprocess
import gdown
from mega import Mega
from terabox_downloader import TeraboxDL
from aiogram.types import FSInputFile
import config

# Initialize Mega (Anonymous)
mega = Mega()
m_client = mega.login()

# --- ENGINE 1: MEGA.NZ ---
def download_mega(url):
    try:
        if not os.path.exists(config.DOWNLOAD_PATH): os.makedirs(config.DOWNLOAD_PATH)
        m_client.download_url(url, config.DOWNLOAD_PATH)
        return True, "Success"
    except Exception as e:
        return False, str(e)

# --- ENGINE 2: TERABOX ---
def download_terabox(url, cookie):
    try:
        client = TeraboxDL(cookie)
        file_info = client.get_file_info(url)
        if not file_info: return False, "Invalid Link/Cookie"
        
        result = client.download(file_info, save_path=config.DOWNLOAD_PATH)
        if isinstance(result, dict) and "error" in result: return False, result["error"]
        return True, config.DOWNLOAD_PATH
    except Exception as e:
        return False, str(e)

# --- ENGINE 3: GOOGLE DRIVE ---
def download_gdrive(url):
    try:
        if not os.path.exists(config.DOWNLOAD_PATH): os.makedirs(config.DOWNLOAD_PATH)
        if "folders" in url:
            gdown.download_folder(url, output=config.DOWNLOAD_PATH, quiet=False, use_cookies=False)
        else:
            gdown.download(url, output=config.DOWNLOAD_PATH + "/", quiet=False, fuzzy=True)
        return True, "Success"
    except Exception as e:
        return False, str(e)

# --- UPLOADER 1: TELEGRAM (VISIBLE) ---
async def send_to_telegram(bot, chat_id, file_path, status_msg):
    try:
        # Check size (Max 1.95GB for Telegram Bots)
        file_size = os.path.getsize(file_path)
        if file_size > 1.95 * 1024 * 1024 * 1024:
            await bot.edit_message_text(f"⚠️ **File too big (>2GB).**\n`{os.path.basename(file_path)}`\nSkipping Telegram upload, moving to Cloud...", chat_id=chat_id, message_id=status_msg.message_id)
            return False

        await bot.edit_message_text(f"📤 **Uploading to Telegram...**\n`{os.path.basename(file_path)}`", chat_id=chat_id, message_id=status_msg.message_id)
        
        # Send as Video if video, else Document
        video_exts = ['.mp4', '.mkv', '.avi', '.mov']
        if any(file_path.lower().endswith(ext) for ext in video_exts):
            await bot.send_video(chat_id, video=FSInputFile(file_path), caption=f"🎬 `{os.path.basename(file_path)}`")
        else:
            await bot.send_document(chat_id, document=FSInputFile(file_path), caption=f"📂 `{os.path.basename(file_path)}`")
        return True
    except Exception as e:
        print(f"Telegram Upload Error: {e}")
        return False

# --- UPLOADER 2: RCLONE (CLOUD) ---
def upload_to_cloud(local_path):
    if not os.listdir(local_path): return False, "Folder Empty"
    try:
        # Move files to cloud and delete local copy
        subprocess.run(["rclone", "move", local_path, config.RCLONE_REMOTE, "--transfers", "4", "--min-age", "1s"], check=True)
        return True, "Done"
    except Exception as e:
        return False, str(e)
        subprocess.run(command, check=True)
        return True, "Upload Complete"
    except subprocess.CalledProcessError as e:
        return False, f"Rclone Error: {e}"
