#!/bin/bash

set -e

# Build Docker images

echo "🛠️ Building Docker images..."
docker-compose build

echo "🧹 Cleaning up old containers..."
docker-compose down -v || true

echo "🚀 Starting up all services (Postgres, Kafka, Spark, FastAPI)..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

echo "🔎 Checking container status:"
docker-compose ps

echo "✅ All services started."
echo "- FastAPI:     http://localhost:8000/docs"
echo "- Postgres:    localhost:5432 (user: admin, pass: admin)"
echo "- Kafka:       localhost:9092"
echo "- Spark UI:    http://localhost:8080 (master), http://localhost:8081 (worker)"
