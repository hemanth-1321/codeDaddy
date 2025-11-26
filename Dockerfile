FROM python:3.12.3-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY server /app/server

RUN pip install --no-cache-dir -r /app/server/requirements.txt \
    && pip install gunicorn uvicorn
