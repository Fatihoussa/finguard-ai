import json
import random
import time
from datetime import datetime
from faker import Faker
from kafka import KafkaProducer

fake = Faker()

# ============================================
# CONFIGURATION
# ============================================
KAFKA_BROKER = "localhost:9092"
TOPIC_NAME   = "finguard-transactions"

# ============================================
# LISTES METIER
# ============================================
CURRENCIES  = ["EUR", "USD", "GBP", "MAD", "CHF"]
MERCHANTS   = ["Amazon", "Carrefour", "Netflix", "Shell",
               "Apple", "Zara", "SNCF", "EDF", "Uber", "Spotify"]
CATEGORIES  = ["shopping", "food", "transport",
               "entertainment", "utilities", "healthcare"]
COUNTRIES   = ["MA", "FR", "ES", "DE", "GB", "US"]
DEVICES     = ["mobile", "desktop", "tablet", "atm"]
STATUSES    = ["completed", "pending", "failed", "refunded"]

# ============================================
# GENERATEUR DE TRANSACTION
# ============================================
def generate_transaction():
    is_fraud = random.random() < 0.03  # 3% de fraudes

    transaction = {
        "transaction_id"  : f"TXN{fake.unique.random_int(min=100000, max=999999)}",
        "client_id"       : f"CLI{random.randint(1, 5000):05d}",
        "amount"          : round(random.uniform(1, 15000) if is_fraud
                                  else random.uniform(1, 2000), 2),
        "currency"        : random.choice(CURRENCIES),
        "merchant"        : random.choice(MERCHANTS),
        "category"        : random.choice(CATEGORIES),
        "country"         : random.choice(COUNTRIES),
        "device"          : random.choice(DEVICES),
        "status"          : random.choice(STATUSES),
        "timestamp"       : datetime.utcnow().isoformat(),
        "is_fraud"        : is_fraud,
        "ip_address"      : fake.ipv4(),
        "lat"             : float(fake.latitude()),
        "lon"             : float(fake.longitude()),
    }
    return transaction

# ============================================
# KAFKA PRODUCER
# ============================================
def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    print(f"🚀 FinGuard Transaction Generator démarré")
    print(f"📡 Topic : {TOPIC_NAME}")
    print(f"─────────────────────────────────────────")

    count = 0
    while True:
        transaction = generate_transaction()
        producer.send(TOPIC_NAME, value=transaction)
        count += 1

        flag = "🚨 FRAUDE" if transaction["is_fraud"] else "✅ OK"
        print(f"[{count}] {flag} | {transaction['transaction_id']} "
              f"| {transaction['client_id']} "
              f"| {transaction['amount']} {transaction['currency']} "
              f"| {transaction['merchant']}")

        time.sleep(0.5)  # 2 transactions par seconde

if __name__ == "__main__":
    main()