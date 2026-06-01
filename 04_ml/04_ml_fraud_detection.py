# Databricks notebook source
# MAGIC %pip install mlflow xgboost scikit-learn imbalanced-learn

# COMMAND ----------

dbutils.library.restartPython()


# COMMAND ----------

# ============================================
# FINGUARD AI — Feature Engineering pour ML
# ============================================

from pyspark.sql.functions import col, when
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml import Pipeline
import mlflow
import mlflow.spark

# Lire depuis Silver
df = spark.table("finguard_silver.transactions_cleaned")

# Encoder les colonnes catégorielles en chiffres
df_ml = df \
    .withColumn("currency_idx",
        when(col("currency") == "EUR", 0)
        .when(col("currency") == "USD", 1)
        .when(col("currency") == "GBP", 2)
        .when(col("currency") == "MAD", 3)
        .otherwise(4)
    ) \
    .withColumn("country_idx",
        when(col("country") == "FR", 0)
        .when(col("country") == "US", 1)
        .when(col("country") == "GB", 2)
        .when(col("country") == "DE", 3)
        .when(col("country") == "ES", 4)
        .otherwise(5)
    ) \
    .withColumn("device_idx",
        when(col("device") == "mobile", 0)
        .when(col("device") == "desktop", 1)
        .when(col("device") == "tablet", 2)
        .otherwise(3)
    ) \
    .withColumn("label", col("is_fraud").cast("int")) \
    .select("amount", "amount_eur", "currency_idx",
            "country_idx", "device_idx", "label")

print(f"✅ Features prêtes : {df_ml.count()} lignes")
display(df_ml.limit(5))

# COMMAND ----------

# ============================================
# Entraînement XGBoost + MLflow Tracking
# ============================================

import mlflow
import mlflow.xgboost
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (classification_report,
                             roc_auc_score, f1_score)
from imblearn.over_sampling import SMOTE

# Convertir en Pandas pour XGBoost
pdf = df_ml.toPandas()
X = pdf[["amount", "amount_eur", "currency_idx",
         "country_idx", "device_idx"]]
y = pdf["label"]

# Gérer le déséquilibre (3% fraudes seulement)
smote = SMOTE(random_state=42)
X_res, y_res = smote.fit_resample(X, y)

# Split train/test
X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42
)

print(f"✅ Train : {len(X_train)} lignes")
print(f"✅ Test  : {len(X_test)} lignes")

# ── MLflow ───────────────────────────────────
mlflow.set_experiment("/Users/houssafatimaezzahrae@gmail.com/FinGuard_Fraud_Detection")

with mlflow.start_run(run_name="XGBoost_v1"):

    params = {
        "n_estimators" : 100,
        "max_depth"    : 5,
        "learning_rate": 0.1,
        "random_state" : 42
    }

    model = xgb.XGBClassifier(**params)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, y_prob)
    f1  = f1_score(y_test, y_pred)

    mlflow.log_params(params)
    mlflow.log_metric("auc_roc", auc)
    mlflow.log_metric("f1_score", f1)
    mlflow.xgboost.log_model(model, "fraud_model")

    print("\n" + "=" * 50)
    print("🤖 RÉSULTATS — XGBoost + MLflow")
    print("=" * 50)
    print(f"✅ AUC-ROC  : {auc:.4f}")
    print(f"✅ F1-Score : {f1:.4f}")
    print("=" * 50)
    print(classification_report(y_test, y_pred,
          target_names=["Normal", "Fraude"]))

# COMMAND ----------

# ============================================
# Sauvegarder les prédictions en Gold Table
# ============================================

import pandas as pd
from pyspark.sql.functions import lit

# Prédictions sur tout le dataset
pdf_full = df_ml.toPandas()
X_full = pdf_full[["amount", "amount_eur", "currency_idx",
                   "country_idx", "device_idx"]]

pdf_full["fraud_score"]      = model.predict_proba(X_full)[:, 1]
pdf_full["fraud_predicted"]  = model.predict(X_full)
pdf_full["risk_score_pct"]   = (pdf_full["fraud_score"] * 100).round(2)

# Convertir en Spark DataFrame
df_predictions = spark.createDataFrame(pdf_full)

# Sauvegarder en Gold Table
df_predictions.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("finguard_gold.fraud_predictions")

print("✅ Gold Table créée : finguard_gold.fraud_predictions")
print(f"✅ Total prédictions : {df_predictions.count()}")

# Résumé
display(df_predictions
    .groupBy("fraud_predicted")
    .count()
    .withColumnRenamed("fraud_predicted", "is_fraud")
    .withColumnRenamed("count", "nb_transactions")
)

# COMMAND ----------

# ============================================
# Exporter le modèle XGBoost
# ============================================

model.save_model("/tmp/fraud_model.json")
print("✅ Modèle sauvegardé dans /tmp/fraud_model.json")

# COMMAND ----------

# Télécharger le modèle
with open("/tmp/fraud_model.json", "rb") as f:
    data = f.read()

with open("/tmp/fraud_model.json", "wb") as f:
    f.write(data)

print("✅ Prêt à télécharger")
displayHTML('<a href="/files/tmp/fraud_model.json">📥 Télécharger fraud_model.json</a>')

# COMMAND ----------

# Sauvegarder le modèle directement en table Delta
model_bytes = open("/tmp/fraud_model.json", "r").read()

model_df = spark.createDataFrame([(model_bytes,)], ["model_json"])
model_df.write \
    .format("delta") \
    .mode("overwrite") \
    .saveAsTable("finguard_gold.fraud_model")

print("✅ Modèle sauvegardé en Delta Table")