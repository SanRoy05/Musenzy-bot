FROM python:3.11-slim

# Install system dependencies
# Added fonts-liberation for beautiful thumbnails
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure cache and downloads directories exist
RUN mkdir -p cache downloads

# Start the bot
CMD ["python", "-m", "MusenzyMusic"]