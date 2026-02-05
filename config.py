import os
from dotenv import load_dotenv

load_dotenv()

# --- 1. TELEGRAM SETTINGS ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# --- 2. QBITTORRENT SETTINGS ---
QBIT_HOST = os.getenv("QBIT_HOST", "localhost")
QBIT_PORT = int(os.getenv("QBIT_PORT", 8080))
QBIT_USER = os.getenv("QBIT_USER", "admin")
QBIT_PASS = os.getenv("QBIT_PASS", "adminadmin")

# --- 3. STORAGE SETTINGS ---
DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH", "./downloads")
RCLONE_REMOTE = os.getenv("RCLONE_REMOTE", "gdrive:Media")

# --- 4. TERABOX COOKIE ---
DEFAULT_TERABOX_COOKIE = os.getenv("DEFAULT_TERABOX_COOKIE", "")
