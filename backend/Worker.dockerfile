FROM python:3.11-slim
RUN apt-get update && apt-get install -y ca-certificates openssl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY run_worker.sh /app/run_worker.sh
COPY backend/health_check_server.py /app/backend/health_check_server.py
RUN chmod +x /app/run_worker.sh
CMD ["/app/run_worker.sh"]