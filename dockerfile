FROM python:3.9-slim

# Install qBittorrent, Rclone, FFmpeg, Curl
RUN apt-get update && apt-get install -y \
    qbittorrent-nox \
    rclone \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install Python Deps
RUN pip install --no-cache-dir -r requirements.txt

# Create Download Folder
RUN mkdir -p /app/downloads

# Executable permission
RUN chmod +x start.sh

CMD ["./start.sh"]
