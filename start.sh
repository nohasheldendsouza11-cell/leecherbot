#!/bin/bash

# 1. Setup Rclone from Render Env Var
mkdir -p /root/.config/rclone
echo "$RCLONE_CONFIG_BASE64" | base64 -d > /root/.config/rclone/rclone.conf

# 2. Start qBittorrent (Port 8090)
qbittorrent-nox -d --webui-port=8090 --confirm-legal-notice

# 3. Start Bot
python bot.py
