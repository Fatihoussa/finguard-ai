# ============================================
# Générer le modèle en local
# ============================================

import random
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE

CURRENCY_MAP = {"EUR": 0, "USD": 1, "GBP": 2, "MAD": 3, "CHF": 4}
COUNTRY_MAP  = {"FR": 0, "US": 1, "GB": 2, "DE": 3, "ES": 4, "MA": 5}
DEVICE_MAP   = {"mobile": 0, "desktop": 1, "tablet": 2, "atm": 3}
CURRENCIES   = list(CURRENCY_MAP.keys())
COUNTRIES    = list(COUNTRY_MAP.keys())
DEVICES      = list(DEVICE_MAP.keys())

# Générer données
rows = []
for i in range(10000):
    is_fraud = random.random() < 0.03
    amount   = round(random.uniform(1, 15000) if is_fraud
                     else random.uniform(1, 2000), 2)
    currency = random.choice(CURRENCIES)
    amount_eur = round(amount * {"EUR":1,"USD":0.92,"GBP":1.17,"MAD":0.093,"CHF":1.04}[currency], 2)
    rows.append({
        "amount"      : amount,
        "amount_eur"  : amount_eur,
        "currency_idx": CURRENCY_MAP[currency],
        "country_idx" : COUNTRY_MAP[random.choice(COUNTRIES)],
        "device_idx"  : DEVICE_MAP[random.choice(DEVICES)],
        "label"       : int(is_fraud)
    })

df = pd.DataFrame(rows)
X  = df.drop("label", axis=1)
y  = df["label"]

# SMOTE + Train
X_res, y_res = SMOTE(random_state=42).fit_resample(X, y)
X_train, X_test, y_train, y_test = train_test_split(
    X_res, y_res, test_size=0.2, random_state=42)

model = xgb.XGBClassifier(n_estimators=100, max_depth=5,
                           learning_rate=0.1, random_state=42)
model.fit(X_train, y_train)
model.save_model("fraud_model.json")

print("✅ fraud_model.json généré dans 05_api/")