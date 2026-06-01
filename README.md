# 🏦 FinGuard AI
![CI/CD](https://github.com/Fatihoussa/finguard-ai/actions/workflows/ci.yml/badge.svg)
### Real-Time FinTech Risk & Fraud Detection Lakehouse Platform

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-3.5-black)
![Databricks](https://img.shields.io/badge/Databricks-Free%20Edition-red)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.0-blue)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal)
![Airflow](https://img.shields.io/badge/Airflow-2.8-blue)
![Docker](https://img.shields.io/badge/Docker-27.3-blue)

---

## 📌 Description

**FinGuard AI** est une plateforme Data Engineering complète dédiée à la détection de fraude bancaire en temps réel.

Elle simule une architecture utilisée dans les banques et fintechs modernes comme Revolut, BNP Paribas ou Société Générale.

---

## 🏗️ Architecture
Transaction Generator → Kafka → Databricks → Bronze → Silver → Gold → XGBoost → FastAPI → Airflow

```

---

## ⚡ Stack Technologique

| Catégorie | Technologies |
|---|---|
| **Streaming** | Apache Kafka, Zookeeper |
| **Processing** | Apache Spark, Databricks |
| **Storage** | Delta Lake, Architecture Medallion |
| **ML** | XGBoost, Scikit-learn, MLflow |
| **API** | FastAPI, Uvicorn |
| **Orchestration** | Apache Airflow |
| **Infrastructure** | Docker, Docker Compose |

---

## 📊 Résultats

| Métrique | Valeur |
|---|---|
| Transactions traitées | 10 000 |
| Taux de fraude simulé | 3% |
| Fraudes détectées | 323 |
| Précision du modèle | 96% |
| AUC-ROC | 0.9956 |
| F1-Score | 0.9618 |
| Durée pipeline Airflow | 35 secondes |

---

## 📁 Structure du projet
```

finguard-ai/ ├── 01_bronze/ │ └── transaction_generator.py ├── 05_api/ │ ├── main.py │ ├── Dockerfile │ └── requirements.txt ├── 06_airflow/ │ └── dags/ │ └── finguard_pipeline.py ├── 08_docker/ │ └── docker-compose-full.yml └── README.md

```

---

## 🚀 Lancement rapide

```bash
# 1. Cloner le projet
git clone https://github.com/Fatihoussa/finguard-ai.git
cd finguard-ai

# 2. Lancer Kafka + Airflow
cd 08_docker
docker-compose -f docker-compose-full.yml up -d

# 3. Lancer FastAPI
cd 05_api
python -m uvicorn main:app --reload --port 8000

# 4. Lancer le générateur
python 01_bronze/transaction_generator.py
```

---

## 🔌 API Endpoints

### POST /predict-risk
```json
{
  "amount": 9500.00,
  "amount_eur": 8740.00,
  "currency": "USD",
  "country": "US",
  "device": "mobile"
}
```

### Response
```json
{
  "fraud_score": 0.9997,
  "is_fraud": true,
  "risk_level": "HIGH",
  "recommendation": "BLOCK"
}
```

---
## 📈 Dashboard

![FinGuard AI Dashboard](architecture/dashboard.png)
## 🌐 Interfaces

| Service | URL |
|---|---|
| Kafka UI | http://localhost:8080 |
| Airflow | http://localhost:8081 |
| FastAPI Docs | http://localhost:8000/docs |

---

## 👩‍💻 Auteur

**Fatima Ezzahrae Houssa** — Data Engineering Student

[![GitHub](https://img.shields.io/badge/GitHub-Fatihoussa-black)](https://github.com/Fatihoussa)
```
