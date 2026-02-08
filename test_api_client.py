import httpx
import asyncio
from datetime import datetime
import random


async def test_api():
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("Testing Fraud Detection FastAPI")
        print("=" * 60)
        
        print("\n1. Health Check")
        print("-" * 60)
        response = await client.get(f"{base_url}/api/v1/health/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        print("\n2. Create Transaction (Low Risk)")
        print("-" * 60)
        low_risk_txn = {
            "step": 1,
            "type": "PAYMENT",
            "amount": 100.50,
            "name_orig": f"C{random.randint(1000000, 9999999)}",
            "oldbalance_org": 5000.00,
            "newbalance_orig": 4899.50,
            "name_dest": f"M{random.randint(1000000, 9999999)}",
            "oldbalance_dest": 1000.00,
            "newbalance_dest": 1100.50,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await client.post(
            f"{base_url}/api/v1/transactions/",
            json=low_risk_txn
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        print("\n3. Create Transaction (High Risk)")
        print("-" * 60)
        high_risk_txn = {
            "step": 1,
            "type": "TRANSFER",
            "amount": 8500.00,
            "name_orig": f"C{random.randint(1000000, 9999999)}",
            "oldbalance_org": 10000.00,
            "newbalance_orig": 1500.00,
            "name_dest": f"M{random.randint(1000000, 9999999)}",
            "oldbalance_dest": 0.00,
            "newbalance_dest": 8500.00,
            "timestamp": datetime.utcnow().isoformat()
        }
        response = await client.post(
            f"{base_url}/api/v1/transactions/",
            json=high_risk_txn
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        print("\n4. Get Recent Transactions")
        print("-" * 60)
        response = await client.get(f"{base_url}/api/v1/transactions/recent?limit=5")
        print(f"Status: {response.status_code}")
        transactions = response.json()
        print(f"Found {len(transactions)} transactions")
        if transactions:
            print(f"Latest: {transactions[0]['type']} - ${transactions[0]['amount']}")
        
        print("\n5. Get Recent Alerts")
        print("-" * 60)
        response = await client.get(f"{base_url}/api/v1/alerts/recent?limit=5")
        print(f"Status: {response.status_code}")
        alerts = response.json()
        print(f"Found {len(alerts)} alerts")
        if alerts:
            print(f"Latest alert: {alerts[0]['type']} - ${alerts[0]['amount']} (Prob: {alerts[0]['probability']:.2%})")
        
        print("\n6. Get High-Risk Alerts")
        print("-" * 60)
        response = await client.get(f"{base_url}/api/v1/alerts/high-risk?threshold=0.7")
        print(f"Status: {response.status_code}")
        high_risk_alerts = response.json()
        print(f"Found {len(high_risk_alerts)} high-risk alerts (>70% probability)")
        
        print("\n" + "=" * 60)
        print("API Testing Complete!")
        print("=" * 60)


if __name__ == "__main__":
    print("\n🧪 Starting API Client Tests...")
    print("Make sure the API server is running: ./start_api.sh\n")
    
    try:
        asyncio.run(test_api())
    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API server.")
        print("Please start the server first: ./start_api.sh")
    except Exception as e:
        print(f"\n❌ Error: {e}")
