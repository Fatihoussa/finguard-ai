# Databricks notebook source
# ============================================
# FINGUARD AI — Gold Layer
# KPIs financiers et analytics métier
# ============================================

from pyspark.sql.functions import (col, sum, count, avg, 
                                    round, desc, when)

# Lire depuis Silver
df_silver = spark.table("finguard_silver.transactions_cleaned")
print(f"📥 Silver chargé : {df_silver.count()} lignes")

# ── KPI 1 : Revenue par pays ──────────────────
kpi_pays = df_silver \
    .filter(col("status") == "completed") \
    .groupBy("country") \
    .agg(
        sum("amount_eur").alias("total_revenue_eur"),
        count("*").alias("nb_transactions"),
        avg("amount_eur").alias("avg_transaction_eur")
    ) \
    .withColumn("total_revenue_eur", round(col("total_revenue_eur"), 2)) \
    .withColumn("avg_transaction_eur", round(col("avg_transaction_eur"), 2)) \
    .orderBy(desc("total_revenue_eur"))

print("\n🌍 KPI 1 — Revenue par pays :")
display(kpi_pays)

# COMMAND ----------

# ── KPI 2 : Fraudes par pays ──────────────────
kpi_fraude = df_silver \
    .groupBy("country") \
    .agg(
        count("*").alias("total_txn"),
        sum(when(col("is_fraud") == True, 1).otherwise(0)).alias("nb_fraudes"),
        sum(when(col("is_fraud") == True, col("amount_eur")).otherwise(0)).alias("montant_fraude_eur")
    ) \
    .withColumn("taux_fraude_pct", round(col("nb_fraudes") / col("total_txn") * 100, 2)) \
    .withColumn("montant_fraude_eur", round(col("montant_fraude_eur"), 2)) \
    .orderBy(desc("taux_fraude_pct"))

print("🚨 KPI 2 — Fraudes par pays :")
display(kpi_fraude)

# ── KPI 3 : Top marchands ─────────────────────
kpi_merchants = df_silver \
    .filter(col("status") == "completed") \
    .groupBy("merchant") \
    .agg(
        sum("amount_eur").alias("total_revenue_eur"),
        count("*").alias("nb_transactions")
    ) \
    .withColumn("total_revenue_eur", round(col("total_revenue_eur"), 2)) \
    .orderBy(desc("total_revenue_eur"))

print("🏪 KPI 3 — Top Marchands :")
display(kpi_merchants)

# COMMAND ----------

# ============================================
# Sauvegarder les Gold Tables
# ============================================

# Gold Table 1 — KPIs par pays
kpi_pays.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("finguard_gold.kpi_revenue_by_country")

# Gold Table 2 — Fraudes par pays
kpi_fraude.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("finguard_gold.kpi_fraud_by_country")

# Gold Table 3 — Top marchands
kpi_merchants.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("finguard_gold.kpi_top_merchants")

print("✅ Gold Tables créées :")
print("   - finguard_gold.kpi_revenue_by_country")
print("   - finguard_gold.kpi_fraud_by_country")
print("   - finguard_gold.kpi_top_merchants")

# Résumé final
print("\n🏆 ARCHITECTURE MEDALLION COMPLÈTE :")
print("   🥉 Bronze : finguard_bronze.transactions_raw")
print("   🥈 Silver : finguard_silver.transactions_cleaned")
print("   🥇 Gold   : finguard_gold.kpi_*")