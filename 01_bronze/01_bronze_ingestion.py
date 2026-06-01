# Databricks notebook source
# ============================================
# FINGUARD AI — Bronze Layer
# Génération et stockage des transactions
# ============================================

import random
from datetime import datetime, timedelta
from pyspark.sql import Row

# Listes métier
CURRENCIES = ["EUR", "USD", "GBP", "MAD", "CHF"]
MERCHANTS  = ["Amazon", "Carrefour", "Netflix", "Shell",
              "Apple", "Zara", "SNCF", "EDF", "Uber", "Spotify"]
CATEGORIES = ["shopping", "food", "transport",
              "entertainment", "utilities", "healthcare"]
COUNTRIES  = ["MA", "FR", "ES", "DE", "GB", "US"]
DEVICES    = ["mobile", "desktop", "tablet", "atm"]
STATUSES   = ["completed", "pending", "failed", "refunded"]

def generate_transactions(n=10000):
    transactions = []
    for i in range(n):
        is_fraud = random.random() < 0.03
        txn = Row(
            transaction_id = f"TXN{i:08d}",
            client_id      = f"CLI{random.randint(1, 5000):05d}",
            amount         = round(random.uniform(1, 15000) if is_fraud
                                   else random.uniform(1, 2000), 2),
            currency       = random.choice(CURRENCIES),
            merchant       = random.choice(MERCHANTS),
            category       = random.choice(CATEGORIES),
            country        = random.choice(COUNTRIES),
            device         = random.choice(DEVICES),
            status         = random.choice(STATUSES),
            timestamp      = (datetime.utcnow() - timedelta(
                                days=random.randint(0, 90),
                                hours=random.randint(0, 23)
                             )).isoformat(),
            is_fraud       = is_fraud
        )
        transactions.append(txn)
    return transactions

# Générer 10 000 transactions
print("⏳ Génération de 10 000 transactions...")
transactions = generate_transactions(10000)
df_bronze = spark.createDataFrame(transactions)

print(f"✅ {df_bronze.count()} transactions générées")
df_bronze.printSchema()

# COMMAND ----------

# ============================================
# Sauvegarder en Bronze Delta Table
# ============================================

df_bronze.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("finguard_bronze.transactions_raw")

print("✅ Bronze Delta Table créée : finguard_bronze.transactions_raw")
print(f"✅ Nombre de lignes : {spark.table('finguard_bronze.transactions_raw').count()}")

# Aperçu des données
display(spark.table("finguard_bronze.transactions_raw").limit(5))

# COMMAND ----------

# ============================================
# Delta Lake Time Travel
# ============================================

# Voir l'historique de la table
print("📜 Historique Delta Lake :")
display(spark.sql("DESCRIBE HISTORY finguard_bronze.transactions_raw"))

# COMMAND ----------

