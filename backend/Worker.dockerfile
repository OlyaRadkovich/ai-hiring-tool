FROM python:3.11-slim
RUN apt-get update && apt-get install -y ca-certificates openssl supervisor && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
CMD uvicorn backend.worker_main:app --host 0.0.0.0 --port ${PORT:-8080}