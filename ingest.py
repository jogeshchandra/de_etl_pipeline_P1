import pandas as pd
import os

# ── Config ─────────────────────────────────────────────
RAW_DATA_PATH = "data/raw/full_grouped.csv"

def ingest_data():
    print("=" * 40)
    print("STEP 1: DATA INGESTION")
    print("=" * 40)

    # ── Check if file exists ────────────────────────────
    if not os.path.exists(RAW_DATA_PATH):
        print(f"ERROR: File not found at {RAW_DATA_PATH}")
        print("Make sure full_grouped.csv is inside data/raw/")
        return None

    # ── Load CSV ────────────────────────────────────────
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"\n✔ File loaded successfully")
    print(f"  Rows    : {df.shape[0]}")
    print(f"  Columns : {df.shape[1]}")

    # ── Column Names ────────────────────────────────────
    print(f"\n--- Column Names ---")
    for col in df.columns:
        print(f"  {col}")

    # ── Data Types ──────────────────────────────────────
    print(f"\n--- Data Types ---")
    print(df.dtypes)

    # ── First 5 Rows ────────────────────────────────────
    print(f"\n--- First 5 Rows ---")
    print(df.head())

    # ── Null Value Check ────────────────────────────────
    print(f"\n--- Null Values Per Column ---")
    print(df.isnull().sum())

    return df

if __name__ == "__main__":
    df = ingest_data()
    if df is not None:
        print("\n✔ Ingestion complete. Ready for filtering.")