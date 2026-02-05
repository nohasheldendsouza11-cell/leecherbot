import os

# --- 1. TELEGRAM SETTINGS ---
# Get from @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" 
# Get from @userinfobot (Security: Only you can use the bot)
ADMIN_ID = 123456789 

# --- 2. QBITTORRENT SETTINGS ---
# Enable Web UI in qBittorrent -> Options -> Web UI
QBIT_HOST = "localhost"
QBIT_PORT = 8080
QBIT_USER = "admin"
QBIT_PASS = "adminadmin"

# --- 3. STORAGE SETTINGS ---
DOWNLOAD_PATH = "./downloads" 
# The exact name of your Rclone remote (run 'rclone listremotes')
RCLONE_REMOTE = "gdrive:Media" 

# --- 4. TERABOX COOKIE ---
# Get 'ndus' cookie from browser dev tools (Application -> Cookies)
DEFAULT_TERABOX_COOKIE = "ndus=YOUR_COOKIE_VALUE_HERE;"
