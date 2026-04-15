"""
Spark Streaming Consumer

Consumes transactions from Kafka, predicts fraud, writes to PostgreSQL.
"""
import os
import pickle
import joblib
import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, to_timestamp, struct
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType,
    IntegerType, FloatType
)

# Configuration
KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "transactions")
MODEL_PATH = os.getenv("MODEL_PATH", "ml/fraud_model.pkl")
FRAUD_THRESHOLD = float(os.getenv("FRAUD_THRESHOLD", "0.5"))

DB_URL = os.getenv("DB_URL", "jdbc:postgresql://localhost:5432/postgres")
DB_PROPS = {
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD", "admin"),
    "driver": "org.postgresql.Driver"
}

SCHEMA = StructType([
    StructField("step", IntegerType()),
    StructField("type", StringType()),
    StructField("amount", DoubleType()),
    StructField("nameOrig", StringType()),
    StructField("oldbalanceOrg", DoubleType()),
    StructField("newbalanceOrig", DoubleType()),
    StructField("nameDest", StringType()),
    StructField("oldbalanceDest", DoubleType()),
    StructField("newbalanceDest", DoubleType()),
    StructField("timestamp", StringType())  # ISO string from producer
])

# All columns for DB write
ALL_COLS = ["step", "type", "amount", "nameOrig", "oldbalanceOrg",
            "newbalanceOrig", "nameDest", "oldbalanceDest", "newbalanceDest"]

# Model features (step, nameOrig, nameDest were dropped during training)
MODEL_FEATURES = ["type", "amount", "oldbalanceOrg", "newbalanceOrig", 
                  "oldbalanceDest", "newbalanceDest"]

# Model singleton
_model = None

def load_model():
    global _model
    if _model is None:
        try:
            with open(MODEL_PATH, "rb") as f:
                _model = pickle.load(f)
        except Exception:
            _model = joblib.load(MODEL_PATH)
    return _model


def predict_fraud_fn(txn_type, amount, old_bal_org, new_bal_org, old_bal_dest, new_bal_dest):
    """Predict fraud using only the features the model was trained on."""
    import pandas as pd
    model = load_model()
    try:
        df = pd.DataFrame([{
            'type': txn_type, 
            'amount': float(amount),
            'oldbalanceOrg': float(old_bal_org),
            'newbalanceOrig': float(new_bal_org),
            'oldbalanceDest': float(old_bal_dest),
            'newbalanceDest': float(new_bal_dest)
        }])
        if hasattr(model, "predict_proba"):
            return float(model.predict_proba(df)[0, 1])
        return float(model.predict(df)[0])
    except Exception:
        return -1.0

predict_fraud = udf(predict_fraud_fn, FloatType())


def save_transactions(batch_df, batch_id):
    batch_df.select(*ALL_COLS, "timestamp") \
        .write.mode("append").jdbc(DB_URL, "transactions", properties=DB_PROPS)


def save_alerts(batch_df, batch_id):
    batch_df.select(
        col("nameOrig"), col("nameDest"), col("amount"), col("type"),
        col("fraud_probability").alias("probability"), col("timestamp")
    ).write.mode("append").jdbc(DB_URL, "alerts", properties=DB_PROPS)


def run():
    spark = SparkSession.builder.appName("FraudDetection").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")  # Only show errors
    
    stream = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .load()
    
    transactions = stream \
        .selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), SCHEMA).alias("data")) \
        .select("data.*") \
        .withColumn("timestamp", to_timestamp(col("timestamp")))
    
    # Use only MODEL_FEATURES for prediction (matches training)
    scored = transactions.withColumn(
        "fraud_probability",
        predict_fraud(
            col("type"), col("amount"), col("oldbalanceOrg"),
            col("newbalanceOrig"), col("oldbalanceDest"), col("newbalanceDest")
        )
    )
    
    alerts = scored.filter(col("fraud_probability") > FRAUD_THRESHOLD)
    
    q1 = scored.writeStream.foreachBatch(save_transactions).start()
    q2 = alerts.writeStream.foreachBatch(save_alerts).start()
    
    print(f"[Consumer] Streaming started (threshold={FRAUD_THRESHOLD})")
    q1.awaitTermination()
    q2.awaitTermination()


if __name__ == "__main__":
    run()
