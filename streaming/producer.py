"""
Kafka Transaction Producer

Generates synthetic transactions and publishes to Kafka.
"""
import os
import json
import time
import random
from datetime import datetime
from confluent_kafka import Producer

KAFKA_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = "transactions"
TRANSACTION_TYPES = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]


def create_producer() -> Producer:
    return Producer({'bootstrap.servers': KAFKA_SERVERS})


def generate_transaction(step: int) -> dict:
    txn_type = random.choice(TRANSACTION_TYPES)
    amount = round(random.uniform(10, 10000), 2)
    
    old_bal_org = round(random.uniform(amount, amount + 50000), 2)
    if txn_type in ["PAYMENT", "TRANSFER", "CASH_OUT"]:
        new_bal_org = round(old_bal_org - amount, 2)
    else:
        new_bal_org = round(old_bal_org + amount, 2)
    
    old_bal_dest = round(random.uniform(0, 50000), 2)
    if txn_type in ["TRANSFER", "CASH_IN"]:
        new_bal_dest = round(old_bal_dest + amount, 2)
    else:
        new_bal_dest = old_bal_dest
    
    return {
        "step": step,
        "type": txn_type,
        "amount": amount,
        "nameOrig": f"C{random.randint(1000000, 9999999)}",
        "oldbalanceOrg": old_bal_org,
        "newbalanceOrig": new_bal_org,
        "nameDest": f"M{random.randint(1000000, 9999999)}",
        "oldbalanceDest": old_bal_dest,
        "newbalanceDest": new_bal_dest,
        "timestamp": datetime.utcnow().isoformat()
    }


def run():
    producer = create_producer()
    step = 1
    
    print(f"[Producer] Publishing to {KAFKA_TOPIC}...")
    
    while True:
        txn = generate_transaction(step)
        try:
            producer.produce(KAFKA_TOPIC, json.dumps(txn).encode('utf-8'))
            producer.flush()
            print(f"Sent: {txn['type']} | ${txn['amount']:.2f}")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(random.uniform(0.1, 0.5))
        if random.random() < 0.05:
            step += 1


if __name__ == "__main__":
    run()
