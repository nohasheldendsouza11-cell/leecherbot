import os
import asyncio
import subprocess
import gdown
from mega import Mega
from terabox_downloader import TeraboxDL
import config

# Initialize Mega (Anonymous)
mega = Mega()
m_client = mega.login()

# --- ENGINE 1: MEGA.NZ ---
def download_mega(url):
    try:
        print(f"☁️ [Mega] Starting: {url}")
        if not os.path.exists(config.DOWNLOAD_PATH):
            os.makedirs(config.DOWNLOAD_PATH)
        m_client.download_url(url, config.DOWNLOAD_PATH)
        return True, "Download successful"
    except Exception as e:
        return False, str(e)

# --- ENGINE 2: TERABOX ---
def download_terabox(url, cookie):
    try:
        print(f"📦 [Terabox] Starting: {url}")
        client = TeraboxDL(cookie)
        file_info = client.get_file_info(url)
        
        if not file_info:
            return False, "Invalid Link or Cookie Expired"
            
        result = client.download(file_info, save_path=config.DOWNLOAD_PATH)
        
        if isinstance(result, dict) and "error" in result:
             return False, result["error"]
             
        return True, config.DOWNLOAD_PATH
    except Exception as e:
        return False, str(e)

# --- ENGINE 3: GOOGLE DRIVE ---
def download_gdrive(url):
    try:
        print(f"🔄 [GDrive] Starting: {url}")
        if not os.path.exists(config.DOWNLOAD_PATH):
            os.makedirs(config.DOWNLOAD_PATH)
            
        if "folders" in url:
            gdown.download_folder(url, output=config.DOWNLOAD_PATH, quiet=False, use_cookies=False)
            return True, config.DOWNLOAD_PATH
        else:
            output = gdown.download(url, output=config.DOWNLOAD_PATH + "/", quiet=False, fuzzy=True)
            if output:
                return True, output
            return False, "Download Failed"
    except Exception as e:
        return False, f"GDrive Error: {str(e)}"

# --- UPLOADER: RCLONE ---
def upload_to_cloud(local_path):
    if not os.listdir(local_path):
        return False, "Folder empty"

    print(f"🚀 [Rclone] Moving files to {config.RCLONE_REMOTE}...")
    try:
        command = [
            "rclone", "move", 
            local_path, 
            config.RCLONE_REMOTE,
            "--transfers", "4",
            "--min-age", "1s",
            "-v"
        ]
        subprocess.run(command, check=True)
        return True, "Upload Complete"
    except subprocess.CalledProcessError as e:
        return False, f"Rclone Error: {e}"
