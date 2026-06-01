# ============================================
# FINGUARD AI — Data Quality
# Great Expectations — 15 règles de validation
# ============================================

import pandas as pd
import great_expectations as gx
import random
from datetime import datetime, timedelta

# ── Générer des données de test ──────────────
def generate_test_data(n=1000):
    rows = []
    for i in range(n):
        is_fraud = random.random() < 0.03
        rows.append({
            "transaction_id" : f"TXN{i:08d}",
            "client_id"      : f"CLI{random.randint(1, 5000):05d}",
            "amount"         : round(random.uniform(1, 15000) if is_fraud
                                     else random.uniform(1, 2000), 2),
            "currency"       : random.choice(["EUR", "USD", "GBP", "MAD", "CHF"]),
            "merchant"       : random.choice(["Amazon", "Carrefour", "Netflix",
                                              "Shell", "Apple", "Zara"]),
            "category"       : random.choice(["shopping", "food", "transport",
                                              "entertainment", "utilities"]),
            "country"        : random.choice(["MA", "FR", "ES", "DE", "GB", "US"]),
            "device"         : random.choice(["mobile", "desktop", "tablet", "atm"]),
            "status"         : random.choice(["completed", "pending",
                                              "failed", "refunded"]),
            "amount_eur"     : round(random.uniform(1, 2000), 2),
            "risk_level"     : random.choice(["LOW", "MEDIUM", "HIGH"]),
            "is_fraud"       : is_fraud
        })
    return pd.DataFrame(rows)

# ── Créer le contexte Great Expectations ─────
print("⏳ Initialisation Great Expectations...")
context = gx.get_context(mode="ephemeral")

# ── Charger les données ───────────────────────
df = generate_test_data(1000)
datasource = context.data_sources.add_pandas("finguard_datasource")
asset = datasource.add_dataframe_asset("transactions")
batch_def = asset.add_batch_definition_whole_dataframe("batch")
batch = batch_def.get_batch(batch_parameters={"dataframe": df})

# ── Créer la Suite de règles ──────────────────
suite = context.suites.add(
    gx.ExpectationSuite(name="finguard_quality_suite")
)

# ── 15 Règles de validation ───────────────────
expectations = [
    # Règle 1 — transaction_id non null
    gx.expectations.ExpectColumnValuesToNotBeNull(column="transaction_id"),
    # Règle 2 — client_id non null
    gx.expectations.ExpectColumnValuesToNotBeNull(column="client_id"),
    # Règle 3 — amount non null
    gx.expectations.ExpectColumnValuesToNotBeNull(column="amount"),
    # Règle 4 — amount positif
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="amount", min_value=0, max_value=100000),
    # Règle 5 — currency valide
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="currency", value_set=["EUR", "USD", "GBP", "MAD", "CHF"]),
    # Règle 6 — country valide
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="country", value_set=["MA", "FR", "ES", "DE", "GB", "US"]),
    # Règle 7 — device valide
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="device", value_set=["mobile", "desktop", "tablet", "atm"]),
    # Règle 8 — status valide
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="status",
        value_set=["completed", "pending", "failed", "refunded"]),
    # Règle 9 — risk_level valide
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="risk_level", value_set=["LOW", "MEDIUM", "HIGH"]),
    # Règle 10 — amount_eur positif
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="amount_eur", min_value=0, max_value=100000),
    # Règle 11 — transaction_id unique
    gx.expectations.ExpectColumnValuesToBeUnique(column="transaction_id"),
    # Règle 12 — colonnes requises présentes
    gx.expectations.ExpectTableColumnsToMatchSet(
        column_set=["transaction_id", "client_id", "amount",
                    "currency", "country", "device", "status",
                    "merchant", "category", "amount_eur",
                    "risk_level", "is_fraud"],
        exact_match=False),
    # Règle 13 — nombre de lignes suffisant
    gx.expectations.ExpectTableRowCountToBeBetween(
        min_value=100, max_value=1000000),
    # Règle 14 — is_fraud non null
    gx.expectations.ExpectColumnValuesToNotBeNull(column="is_fraud"),
    # Règle 15 — merchant non null
    gx.expectations.ExpectColumnValuesToNotBeNull(column="merchant"),
]

for exp in expectations:
    suite.add_expectation(exp)

# ── Validation ────────────────────────────────
validation_def = context.validation_definitions.add(
    gx.ValidationDefinition(
        name="finguard_validation",
        data=batch_def,
        suite=suite
    )
)

results = validation_def.run(batch_parameters={"dataframe": df})

# ── Rapport ───────────────────────────────────
print("\n" + "=" * 55)
print("📊 FINGUARD AI — DATA QUALITY REPORT")
print("=" * 55)
print(f"✅ Règles validées  : {results.statistics['successful_expectations']}")
print(f"❌ Règles échouées  : {results.statistics['unsuccessful_expectations']}")
print(f"📈 Score qualité    : {results.statistics['success_percent']:.1f}%")
print(f"📦 Lignes analysées : {len(df):,}")
print("=" * 55)

if results.success:
    print("🎉 TOUTES LES RÈGLES SONT VALIDÉES !")
else:
    print("⚠️  Certaines règles ont échoué !")