FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data/fishmap/images/backup /data/fishmap/images/recycle /data/fishmap/db

EXPOSE 2026

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "2026"]
