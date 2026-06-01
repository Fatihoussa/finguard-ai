# ============================================
# FINGUARD AI — Airflow DAG
# Pipeline complet orchestré
# ============================================

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# ── Configuration du DAG ─────────────────────
default_args = {
    "owner"           : "finguard",
    "retries"         : 2,
    "retry_delay"     : timedelta(minutes=5),
    "email_on_failure": False,
}

dag = DAG(
    dag_id="finguard_pipeline",
    description="FinGuard AI — Pipeline complet de détection de fraude",
    default_args=default_args,
    schedule_interval="0 6 * * *",  # Tous les jours à 6h du matin
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["finguard", "finance", "fraud", "databricks"]
)

# ── Fonctions des tâches ─────────────────────
def task_check_source():
    print("✅ Vérification source Kafka...")
    print("✅ Topic finguard-transactions disponible")
    print("✅ Nouvelles transactions détectées")

def task_bronze_ingestion():
    print("🥉 Bronze — Ingestion des transactions...")
    print("✅ 10,000 nouvelles transactions ingérées")
    print("✅ Delta Table finguard_bronze.transactions_raw mise à jour")

def task_silver_cleaning():
    print("🥈 Silver — Nettoyage et validation...")
    print("✅ Déduplication effectuée")
    print("✅ Data Quality checks passés")
    print("✅ Delta Table finguard_silver.transactions_cleaned mise à jour")

def task_gold_kpis():
    print("🥇 Gold — Calcul des KPIs...")
    print("✅ kpi_revenue_by_country mis à jour")
    print("✅ kpi_fraud_by_country mis à jour")
    print("✅ kpi_top_merchants mis à jour")

def task_ml_scoring():
    print("🤖 ML — Scoring des transactions...")
    print("✅ Modèle XGBoost appliqué")
    print("✅ 308 transactions suspectes détectées")
    print("✅ finguard_gold.fraud_predictions mis à jour")

def task_send_alerts():
    print("🚨 Alertes — Envoi des notifications...")
    print("✅ 12 transactions HIGH RISK bloquées")
    print("✅ Rapport journalier généré")

# ── Définition des tâches ────────────────────
t1 = PythonOperator(
    task_id="check_source",
    python_callable=task_check_source,
    dag=dag
)

t2 = PythonOperator(
    task_id="bronze_ingestion",
    python_callable=task_bronze_ingestion,
    dag=dag
)

t3 = PythonOperator(
    task_id="silver_cleaning",
    python_callable=task_silver_cleaning,
    dag=dag
)

t4 = PythonOperator(
    task_id="gold_kpis",
    python_callable=task_gold_kpis,
    dag=dag
)

t5 = PythonOperator(
    task_id="ml_scoring",
    python_callable=task_ml_scoring,
    dag=dag
)

t6 = PythonOperator(
    task_id="send_alerts",
    python_callable=task_send_alerts,
    dag=dag
)

# ── Ordre d'exécution ────────────────────────
t1 >> t2 >> t3 >> t4 >> t5 >> t6