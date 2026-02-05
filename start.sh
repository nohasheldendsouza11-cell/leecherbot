#!/bin/bash

# 1. Setup Rclone Config from Env Variable
# We decode the base64 config variable and save it to the default rclone config location
mkdir -p ~/.config/rclone
echo "$RCLONE_CONFIG_BASE64" | base64 -d > ~/.config/rclone/rclone.conf

# 2. Start qBittorrent in background
# We run it as a daemon (-d) listening on 8080
qbittorrent-nox -d --webui-port=8080 --confirm-legal-notice

# 3. Start the Python Bot
python bot.py
