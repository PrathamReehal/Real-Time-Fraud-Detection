FROM python:3.11-slim

WORKDIR /app

# System dependencies (NO Java needed for Kafka Python client)
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    libpq-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["bash", "./start_api.sh"]
