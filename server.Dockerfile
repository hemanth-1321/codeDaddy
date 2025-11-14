FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY server /app/server

RUN pip install --no-cache-dir -r /app/server/requirements.txt


CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]