import os
import pickle
import joblib
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, pandas_udf
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType, FloatType
from datetime import datetime

# Kafka and DB config (edit as needed or use env vars)
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "transactions")
DB_URL = os.getenv("DB_URL", "jdbc:postgresql://localhost:5432/postgres")
DB_PROPERTIES = {
    "user": os.getenv("DB_USER", "prathamreehal"),
    "password": os.getenv("DB_PASSWORD", "admin"),
    "driver": "org.postgresql.Driver"
}
MODEL_PATH = os.getenv("MODEL_PATH", "../ml_models/fraud_detection_pipeline.pkl")
FRAUD_THRESHOLD = float(os.getenv("FRAUD_THRESHOLD", "0.5"))

# Schema matching PaySim
schema = StructType([
    StructField("step", IntegerType(), True),
    StructField("type", StringType(), True),
    StructField("amount", DoubleType(), True),
    StructField("nameOrig", StringType(), True),
    StructField("oldbalanceOrg", DoubleType(), True),
    StructField("newbalanceOrig", DoubleType(), True),
    StructField("nameDest", StringType(), True),
    StructField("oldbalanceDest", DoubleType(), True),
    StructField("newbalanceDest", DoubleType(), True),
    StructField("timestamp", TimestampType(), True)
])

pipeline_model = None

def get_model():
    global pipeline_model
    if pipeline_model is None:
        try:
            with open(MODEL_PATH, "rb") as f:
                pipeline_model = pickle.load(f)
        except Exception:
            pipeline_model = joblib.load(MODEL_PATH)
    return pipeline_model

@pandas_udf(FloatType())
def predict_fraud(step, type_col, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest):
    data = pd.DataFrame({
        'step': step,
        'type': type_col,
        'amount': amount,
        'nameOrig': nameOrig,
        'oldbalanceOrg': oldbalanceOrg,
        'newbalanceOrig': newbalanceOrig,
        'nameDest': nameDest,
        'oldbalanceDest': oldbalanceDest,
        'newbalanceDest': newbalanceDest
    })
    model = get_model()
    try:
        if hasattr(model, "predict_proba"):
            preds = model.predict_proba(data)[:, 1]
        else:
            preds = model.predict(data)
    except Exception:
        return pd.Series([-1.0] * len(data))
    return pd.Series(preds)

def write_txns_to_db(batch_df, batch_id):
    batch_df.select(
        "step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig", "nameDest", "oldbalanceDest", "newbalanceDest", "timestamp"
    ).write.mode("append").jdbc(DB_URL, "transactions", properties=DB_PROPERTIES)

def write_alerts_to_db(batch_df, batch_id):
    batch_df.select(
        col("nameOrig"), col("nameDest"), col("amount"), col("type"),
        col("fraud_probability").alias("probability"), col("timestamp")
    ).write.mode("append").jdbc(DB_URL, "alerts", properties=DB_PROPERTIES)

def main():
    spark = SparkSession.builder.appName("BackgroundFraudDetection").getOrCreate()
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .load()
    parsed_df = df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col("value"), schema).alias("data")) \
        .select("data.*")
    scored_df = parsed_df.withColumn("fraud_probability", predict_fraud(
        col("step"), col("type"), col("amount"), col("nameOrig"), col("oldbalanceOrg"),
        col("newbalanceOrig"), col("nameDest"), col("oldbalanceDest"), col("newbalanceDest")
    ))
    alerts_df = scored_df.filter(col("fraud_probability") > FRAUD_THRESHOLD)
    q1 = scored_df.writeStream.foreachBatch(write_txns_to_db).start()
    q2 = alerts_df.writeStream.foreachBatch(write_alerts_to_db).start()
    print("[SparkService] Streaming started. Press Ctrl+C to exit.")
    q1.awaitTermination()
    q2.awaitTermination()

if __name__ == "__main__":
    main()
