from kafka import KafkaProducer
import json, time, random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

# Configuration
TARGET_TPS = 10000  # Transactions per second
BATCH_SIZE = 1000   # Send in batches for better performance
NUM_THREADS = 10    # Number of producer threads

# Mock data for realism
CITIES = ["New York", "San Francisco", "London", "Paris", "Tokyo", "Mumbai", "Berlin"]
CATEGORIES = ["Entertainment", "Food", "Tech", "Luxury", "Travel", "Groceries"]
DEVICES = ["iPhone", "Android", "MacBook", "Windows", "Unknown"]
TYPES = ["PAYMENT", "TRANSFER", "CASH_OUT", "DEBIT", "CASH_IN"]

# Shared counter for statistics
stats_lock = threading.Lock()
total_sent = 0
start_time = time.time()

def create_producer():
    """Create a Kafka producer with optimized settings for high throughput"""
    return KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        # Performance optimizations
        batch_size=16384,           # Larger batch size
        linger_ms=10,               # Wait up to 10ms to batch messages
        compression_type='lz4',     # Enable compression
        acks=1,                     # Wait for leader acknowledgment only
        buffer_memory=33554432,     # 32MB buffer
        max_in_flight_requests_per_connection=5
    )

def generate_transaction(step):
    """Generate a single transaction"""
    txn_type = random.choice(TYPES)
    amount = round(random.uniform(10, 10000), 2)
    name_orig = f"C{random.randint(1000000, 9999999)}"
    name_dest = f"M{random.randint(1000000, 9999999)}"
    
    # Simulate realistic balances
    old_balance_org = round(random.uniform(amount, amount + 50000), 2)
    new_balance_orig = round(old_balance_org - amount, 2) if txn_type in ["PAYMENT", "TRANSFER", "CASH_OUT"] else round(old_balance_org + amount, 2)
    
    old_balance_dest = round(random.uniform(0, 50000), 2)
    new_balance_dest = round(old_balance_dest + amount, 2) if txn_type in ["TRANSFER", "CASH_IN"] else old_balance_dest

    return {
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

def send_batch(producer, batch, step):
    """Send a batch of transactions"""
    global total_sent
    
    futures = []
    for _ in range(batch):
        txn = generate_transaction(step)
        future = producer.send("transactions", txn)
        futures.append(future)
    
    # Wait for all messages in batch to be sent
    for future in futures:
        try:
            future.get(timeout=10)
        except Exception as e:
            print(f"❌ Error sending message: {e}")
    
    with stats_lock:
        total_sent += batch

def producer_worker(worker_id, transactions_per_worker):
    """Worker thread that sends transactions"""
    producer = create_producer()
    step = 1
    
    print(f"🚀 Worker {worker_id} started (target: {transactions_per_worker} TPS)")
    
    try:
        while True:
            batch_start = time.time()
            
            # Send transactions for this second
            batches = transactions_per_worker // BATCH_SIZE
            remainder = transactions_per_worker % BATCH_SIZE
            
            for _ in range(batches):
                send_batch(producer, BATCH_SIZE, step)
            
            if remainder > 0:
                send_batch(producer, remainder, step)
            
            # Increment step occasionally
            if random.random() < 0.05:
                step += 1
            
            # Sleep to maintain target TPS
            elapsed = time.time() - batch_start
            sleep_time = max(0, 1.0 - elapsed)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print(f"Worker {worker_id} stopping...")
    finally:
        producer.close()

def stats_reporter():
    """Print statistics every second"""
    global total_sent, start_time
    
    while True:
        time.sleep(1)
        elapsed = time.time() - start_time
        with stats_lock:
            current_total = total_sent
        
        tps = current_total / elapsed if elapsed > 0 else 0
        print(f"📊 Total: {current_total:,} | TPS: {tps:,.0f} | Elapsed: {elapsed:.1f}s")

if __name__ == "__main__":
    print("=" * 60)
    print(f"🔥 HIGH-THROUGHPUT KAFKA PRODUCER")
    print(f"Target: {TARGET_TPS:,} transactions/second")
    print(f"Threads: {NUM_THREADS}")
    print(f"Batch Size: {BATCH_SIZE}")
    print("=" * 60)
    print()
    
    # Calculate transactions per worker
    transactions_per_worker = TARGET_TPS // NUM_THREADS
    
    # Start stats reporter in background
    stats_thread = threading.Thread(target=stats_reporter, daemon=True)
    stats_thread.start()
    
    # Start producer workers
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = []
        for i in range(NUM_THREADS):
            future = executor.submit(producer_worker, i, transactions_per_worker)
            futures.append(future)
        
        try:
            # Wait for all workers
            for future in futures:
                future.result()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down gracefully...")
            print(f"📈 Final Stats: {total_sent:,} transactions sent")
