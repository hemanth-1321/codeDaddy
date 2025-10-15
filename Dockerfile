# Dockerfile.worker
FROM python:3.11-slim

WORKDIR /app

# Install git and any system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy your worker code
COPY server /app/server

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/server/requirements.txt

