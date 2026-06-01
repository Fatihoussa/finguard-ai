# ============================================
# FINGUARD AI — Tests Unitaires
# test_api.py — Tests de l'API FastAPI
# ============================================

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Aller dans le bon dossier pour trouver le modèle
os.chdir(os.path.join(os.path.dirname(__file__), '..', '05_api'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '05_api'))
from main import app

client = TestClient(app)

# ── Tests ─────────────────────────────────────
def test_root_endpoint():
    """Test 1 — L'API répond sur /"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
    print("✅ Test 1 passed — Root endpoint OK")

def test_health_endpoint():
    """Test 2 — L'endpoint /health fonctionne"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Test 2 passed — Health endpoint OK")

def test_predict_risk_normal():
    """Test 3 — Transaction normale"""
    response = client.post("/predict-risk", json={
        "amount"    : 50.0,
        "amount_eur": 46.0,
        "currency"  : "EUR",
        "country"   : "FR",
        "device"    : "mobile"
    })
    assert response.status_code == 200
    data = response.json()
    assert "fraud_score" in data
    assert "is_fraud" in data
    assert "risk_level" in data
    assert "recommendation" in data
    print("✅ Test 3 passed — Prédiction normale OK")

def test_predict_risk_fraud():
    """Test 4 — Transaction suspecte"""
    response = client.post("/predict-risk", json={
        "amount"    : 9500.0,
        "amount_eur": 8740.0,
        "currency"  : "USD",
        "country"   : "US",
        "device"    : "mobile"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["fraud_score"] > 0.5
    assert data["recommendation"] == "BLOCK"
    print("✅ Test 4 passed — Fraude détectée OK")

def test_fraud_score_range():
    """Test 5 — Le fraud score est entre 0 et 1"""
    response = client.post("/predict-risk", json={
        "amount"    : 100.0,
        "amount_eur": 92.0,
        "currency"  : "USD",
        "country"   : "FR",
        "device"    : "desktop"
    })
    assert response.status_code == 200
    score = response.json()["fraud_score"]
    assert 0 <= score <= 1
    print("✅ Test 5 passed — Fraud score valide")

def test_risk_level_values():
    """Test 6 — Risk level est LOW/MEDIUM/HIGH"""
    response = client.post("/predict-risk", json={
        "amount"    : 500.0,
        "amount_eur": 460.0,
        "currency"  : "EUR",
        "country"   : "MA",
        "device"    : "atm"
    })
    assert response.status_code == 200
    risk = response.json()["risk_level"]
    assert risk in ["LOW", "MEDIUM", "HIGH"]
    print("✅ Test 6 passed — Risk level valide")

def test_recommendation_values():
    """Test 7 — Recommendation est APPROVE/BLOCK"""
    response = client.post("/predict-risk", json={
        "amount"    : 200.0,
        "amount_eur": 184.0,
        "currency"  : "GBP",
        "country"   : "GB",
        "device"    : "tablet"
    })
    assert response.status_code == 200
    rec = response.json()["recommendation"]
    assert rec in ["APPROVE", "BLOCK"]
    print("✅ Test 7 passed — Recommendation valide")

def test_invalid_request():
    """Test 8 — Requête invalide retourne erreur"""
    response = client.post("/predict-risk", json={
        "amount": "invalid"
    })
    assert response.status_code == 422
    print("✅ Test 8 passed — Validation erreur OK")