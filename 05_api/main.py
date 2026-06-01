# ============================================
# FINGUARD AI — FastAPI
# API de détection de fraude
# ============================================

from fastapi import FastAPI
from pydantic import BaseModel
import xgboost as xgb
import pandas as pd
import numpy as np

app = FastAPI(
    title="FinGuard AI — Fraud Detection API",
    description="API de détection de fraude bancaire en temps réel",
    version="1.0.0"
)

# ── Charger le modèle ────────────────────────
model = xgb.XGBClassifier()
model.load_model("fraud_model.json")

# ── Schéma de la requête ─────────────────────
class Transaction(BaseModel):
    amount: float
    amount_eur: float
    currency: str
    country: str
    device: str

# ── Encodeurs ────────────────────────────────
CURRENCY_MAP = {"EUR": 0, "USD": 1, "GBP": 2, "MAD": 3, "CHF": 4}
COUNTRY_MAP  = {"FR": 0, "US": 1, "GB": 2, "DE": 3, "ES": 4, "MA": 5}
DEVICE_MAP   = {"mobile": 0, "desktop": 1, "tablet": 2, "atm": 3}

# ── Endpoints ────────────────────────────────
@app.get("/")
def root():
    return {
        "message"  : "FinGuard AI — Fraud Detection API",
        "version"  : "1.0.0",
        "status"   : "running"
    }

@app.post("/predict-risk")
def predict_risk(txn: Transaction):
    features = pd.DataFrame([{
        "amount"      : txn.amount,
        "amount_eur"  : txn.amount_eur,
        "currency_idx": CURRENCY_MAP.get(txn.currency, 4),
        "country_idx" : COUNTRY_MAP.get(txn.country, 5),
        "device_idx"  : DEVICE_MAP.get(txn.device, 3)
    }])

    fraud_score = model.predict_proba(features)[0][1]
    is_fraud    = bool(fraud_score > 0.5)

    risk_level = (
        "HIGH"   if fraud_score > 0.7 else
        "MEDIUM" if fraud_score > 0.4 else
        "LOW"
    )

    return {
        "transaction"  : txn.dict(),
        "fraud_score"  : round(float(fraud_score), 4),
        "is_fraud"     : is_fraud,
        "risk_level"   : risk_level,
        "recommendation": "BLOCK" if is_fraud else "APPROVE"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "model": "XGBoost v1"}