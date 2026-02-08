from kafka import KafkaProducer
import json, time, random
import os
from datetime import datetime

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    api_version_auto_timeout_ms=3000
)

# Mock data for realism
CITIES = ["New York", "San Francisco", "London", "Paris", "Tokyo", "Mumbai", "Berlin"]
CATEGORIES = ["Entertainment", "Food", "Tech", "Luxury", "Travel", "Groceries"]
DEVICES = ["iPhone", "Android", "MacBook", "Windows", "Unknown"]

TYPES = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]

step = 1

while True:
    # Simulate PaySim schema
    txn_type = random.choice(TYPES)
    amount = round(random.uniform(10, 10000), 2)
    name_orig = f"C{random.randint(1000000, 9999999)}"
    name_dest = f"M{random.randint(1000000, 9999999)}"
    
    # Simulate realistic balances
    old_balance_org = round(random.uniform(amount, amount + 50000), 2)
    new_balance_orig = round(old_balance_org - amount, 2) if txn_type in ["PAYMENT", "TRANSFER", "CASH_OUT"] else round(old_balance_org + amount, 2)
    
    old_balance_dest = round(random.uniform(0, 50000), 2)
    new_balance_dest = round(old_balance_dest + amount, 2) if txn_type in ["TRANSFER", "CASH_IN"] else old_balance_dest

    # Introduce fraud patterns for testing
    # Pattern: Large TRANSFER followed by CASH_OUT is often fraud in this dataset
    # But for now we just send raw data
    
    txn = {
        "step": step,
        "type": txn_type,
        "amount": amount,
        "nameOrig": name_orig,
        "oldbalanceOrg": old_balance_org,
        "newbalanceOrig": new_balance_orig,
        "nameDest": name_dest,
        "oldbalanceDest": old_balance_dest,
        "newbalanceDest": new_balance_dest,
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        future = producer.send("transactions", txn)
        record_metadata = future.get(timeout=10)
        
        print(f"Sent: {txn['type']} | Amount: {txn['amount']} | Orig: {txn['nameOrig']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

    # Random sleep
    time.sleep(random.uniform(0.1, 0.5))
    
    # Increment step occasionally to simulate time passing (1 step = 1 hour in PaySim)
    if random.random() < 0.05:
        step += 1
