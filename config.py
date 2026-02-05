import os
from dotenv import load_dotenv

load_dotenv()

# --- 1. TELEGRAM SETTINGS ---
# Reads from Render Env Vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# --- 2. QBITTORRENT SETTINGS ---
# 'localhost' works because qBit runs in the same Docker container
QBIT_HOST = "localhost"
QBIT_PORT = int(os.getenv("QBIT_PORT", 8090))
QBIT_USER = os.getenv("QBIT_USER", "admin")
QBIT_PASS = os.getenv("QBIT_PASS", "adminadmin")

# --- 3. STORAGE SETTINGS ---
DOWNLOAD_PATH = "./downloads"
RCLONE_REMOTE = os.getenv("RCLONE_REMOTE", "gdrive:Media")

# --- 4. FEATURES ---
# True = Send file to Telegram Chat (if <2GB). False = Cloud only.
UPLOAD_TO_TELEGRAM = True 

# --- 5. TERABOX COOKIE ---
DEFAULT_TERABOX_COOKIE = os.getenv("DEFAULT_TERABOX_COOKIE", "")"")
