# Real-Time Fraud Detection System

Real-time fraud detection using FastAPI, Spark Streaming, Kafka, and PostgreSQL.

## Architecture

```
Producer → Kafka → Spark Consumer → PostgreSQL
                        ↓
                    ML Model
                        ↓
                 FastAPI (REST API)
```

## Project Structure

```
├── app/                  # FastAPI application
│   ├── main.py          # Routes & app entry
│   ├── models.py        # Domain models
│   ├── schemas.py       # API schemas
│   ├── database.py      # DB & repositories
│   ├── service.py       # Business logic
│   └── config.py        # Settings
├── streaming/           # Stream processing
│   ├── consumer.py      # Spark streaming job
│   └── producer.py      # Kafka producer
├── scripts/
│   └── train.py         # Model training
├── ml/                  # ML model
├── db/
│   └── init.sql         # DB schema
├── docker-compose.yml
└── requirements.txt
```

## Quick Start

```bash
docker-compose up -d
```

**Services:**
- API: http://localhost:8000/docs
- Spark UI: http://localhost:8080

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/transactions` | Create & predict |
| GET | `/api/v1/transactions/recent` | Recent transactions |
| GET | `/api/v1/transactions/{id}` | Get by ID |
| GET | `/api/v1/alerts/recent` | Recent alerts |
| GET | `/api/v1/alerts/high-risk` | High-risk alerts |
| GET | `/api/v1/health` | Health check |

## Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Environment Variables

```
DB_HOST=localhost
DB_USER=admin
DB_PASSWORD=admin
MODEL_PATH=ml/fraud_model.pkl
FRAUD_THRESHOLD=0.5
```

## Tech Stack

- **FastAPI** - Async REST API
- **asyncpg** - PostgreSQL driver
- **Spark Streaming** - Real-time processing
- **Kafka** - Message broker
- **scikit-learn** - ML model
- **Docker** - Containerization
