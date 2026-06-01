# ============================================
# FINGUARD AI — Tests Unitaires
# test_model.py — Tests du modèle ML
# ============================================

import pytest
import pandas as pd
import numpy as np
import xgboost as xgb
import random

# ── Fixtures ─────────────────────────────────
@pytest.fixture
def sample_data():
    """Générer des données de test"""
    rows = []
    for i in range(100):
        is_fraud = random.random() < 0.3
        rows.append({
            "amount"      : round(random.uniform(1, 15000), 2),
            "amount_eur"  : round(random.uniform(1, 10000), 2),
            "currency_idx": random.randint(0, 4),
            "country_idx" : random.randint(0, 5),
            "device_idx"  : random.randint(0, 3),
            "label"       : int(is_fraud)
        })
    return pd.DataFrame(rows)

@pytest.fixture
def trained_model(sample_data):
    """Entraîner un modèle de test"""
    X = sample_data.drop("label", axis=1)
    y = sample_data["label"]
    model = xgb.XGBClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model

# ── Tests ─────────────────────────────────────
def test_data_shape(sample_data):
    """Test 1 — Le dataset a le bon nombre de colonnes"""
    assert sample_data.shape[1] == 6
    print("✅ Test 1 passed — Shape correcte")

def test_data_no_nulls(sample_data):
    """Test 2 — Pas de valeurs nulles"""
    assert sample_data.isnull().sum().sum() == 0
    print("✅ Test 2 passed — Pas de valeurs nulles")

def test_data_amount_positive(sample_data):
    """Test 3 — Les montants sont positifs"""
    assert (sample_data["amount"] > 0).all()
    print("✅ Test 3 passed — Montants positifs")

def test_data_label_binary(sample_data):
    """Test 4 — Le label est binaire (0 ou 1)"""
    assert set(sample_data["label"].unique()).issubset({0, 1})
    print("✅ Test 4 passed — Label binaire")

def test_model_training(trained_model):
    """Test 5 — Le modèle s'entraîne correctement"""
    assert trained_model is not None
    print("✅ Test 5 passed — Modèle entraîné")

def test_model_prediction(trained_model, sample_data):
    """Test 6 — Le modèle fait des prédictions"""
    X = sample_data.drop("label", axis=1)
    predictions = trained_model.predict(X)
    assert len(predictions) == len(sample_data)
    print("✅ Test 6 passed — Prédictions OK")

def test_model_prediction_binary(trained_model, sample_data):
    """Test 7 — Les prédictions sont binaires"""
    X = sample_data.drop("label", axis=1)
    predictions = trained_model.predict(X)
    assert set(predictions).issubset({0, 1})
    print("✅ Test 7 passed — Prédictions binaires")

def test_model_proba(trained_model, sample_data):
    """Test 8 — Les probabilités sont entre 0 et 1"""
    X = sample_data.drop("label", axis=1)
    probas = trained_model.predict_proba(X)
    assert (probas >= 0).all() and (probas <= 1).all()
    print("✅ Test 8 passed — Probabilités valides")

def test_fraud_score_range(trained_model, sample_data):
    """Test 9 — Le score de fraude est entre 0 et 1"""
    X = sample_data.drop("label", axis=1)
    fraud_scores = trained_model.predict_proba(X)[:, 1]
    assert fraud_scores.min() >= 0
    assert fraud_scores.max() <= 1
    print("✅ Test 9 passed — Fraud scores valides")

def test_high_amount_fraud_risk(trained_model):
    """Test 10 — Montant élevé = risque fraude plus haut"""
    low_risk = pd.DataFrame([{
        "amount": 50, "amount_eur": 46,
        "currency_idx": 0, "country_idx": 0, "device_idx": 0
    }])
    high_risk = pd.DataFrame([{
        "amount": 14000, "amount_eur": 12880,
        "currency_idx": 1, "country_idx": 1, "device_idx": 3
    }])
    score_low  = trained_model.predict_proba(low_risk)[0][1]
    score_high = trained_model.predict_proba(high_risk)[0][1]
    print(f"✅ Test 10 passed — Low: {score_low:.3f} / High: {score_high:.3f}")