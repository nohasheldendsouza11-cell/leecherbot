# Use Python slim image
FROM python:3.9-slim

# Install system dependencies (qBittorrent, Rclone, FFmpeg)
RUN apt-get update && apt-get install -y \
    qbittorrent-nox \
    rclone \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all bot files
COPY . .

# Create downloads folder
RUN mkdir -p /app/downloads

# Expose ports (Optional, mostly for qBit WebUI if needed)
EXPOSE 8080

# Command to run: Setup Rclone config -> Start qBit -> Start Bot
CMD ["bash", "start.sh"]
