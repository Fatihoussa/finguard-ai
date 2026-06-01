# Databricks notebook source
# ============================================
# FINGUARD AI — Silver Layer
# Nettoyage et validation des données
# ============================================

from pyspark.sql.functions import col, to_timestamp, when, trim, upper

# Lire depuis Bronze
df_bronze = spark.table("finguard_bronze.transactions_raw")

print(f"📥 Bronze — Lignes chargées : {df_bronze.count()}")
print(f"📥 Colonnes nulles avant nettoyage :")
display(df_bronze.select([col(c).isNull().cast("int").alias(c) 
                          for c in df_bronze.columns]).agg(
    *[__import__('pyspark.sql.functions', fromlist=['sum']).sum(c).alias(c) 
      for c in df_bronze.columns]
))

# COMMAND ----------

# ============================================
# Nettoyage + Enrichissement Silver
# ============================================

from pyspark.sql.functions import (col, to_timestamp, when, 
                                    trim, upper, round, lit,
                                    current_timestamp)

df_silver = df_bronze \
    .withColumn("timestamp", to_timestamp(col("timestamp"))) \
    .withColumn("amount", round(col("amount"), 2)) \
    .withColumn("currency", upper(trim(col("currency")))) \
    .withColumn("country", upper(trim(col("country")))) \
    .withColumn("status", trim(col("status"))) \
    .withColumn("amount_eur",
        when(col("currency") == "USD", round(col("amount") * 0.92, 2))
        .when(col("currency") == "GBP", round(col("amount") * 1.17, 2))
        .when(col("currency") == "MAD", round(col("amount") * 0.093, 2))
        .when(col("currency") == "CHF", round(col("amount") * 1.04, 2))
        .otherwise(col("amount"))
    ) \
    .withColumn("risk_level",
        when(col("amount_eur") > 5000, "HIGH")
        .when(col("amount_eur") > 1000, "MEDIUM")
        .otherwise("LOW")
    ) \
    .withColumn("ingestion_time", current_timestamp()) \
    .dropDuplicates(["transaction_id"])

print(f"✅ Silver — Lignes après nettoyage : {df_silver.count()}")
print(f"✅ Nouvelles colonnes : amount_eur, risk_level, ingestion_time")
display(df_silver.limit(5))

# COMMAND ----------

# ============================================
# Data Quality Checks + Sauvegarde Silver
# ============================================

# Vérifications qualité
total = df_silver.count()
completed = df_silver.filter(col("status") == "completed").count()
high_risk  = df_silver.filter(col("risk_level") == "HIGH").count()
fraud      = df_silver.filter(col("is_fraud") == True).count()
invalid    = df_silver.filter(
    (col("amount") <= 0) | col("transaction_id").isNull()
).count()

print("=" * 50)
print("📊 DATA QUALITY REPORT — Silver Layer")
print("=" * 50)
print(f"✅ Total transactions    : {total:,}")
print(f"✅ Transactions OK       : {completed:,} ({completed/total*100:.1f}%)")
print(f"🔴 Transactions HIGH risk: {high_risk:,} ({high_risk/total*100:.1f}%)")
print(f"🚨 Fraudes détectées     : {fraud:,} ({fraud/total*100:.1f}%)")
print(f"❌ Données invalides     : {invalid:,}")
print("=" * 50)

# Sauvegarder en Silver Delta Table
df_silver.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("finguard_silver.transactions_cleaned")

print("✅ Silver Delta Table créée : finguard_silver.transactions_cleaned")