import pandas as pd
import os
from ingest import ingest_data

# ── Config
RAW_DATA_PATH = "data/raw/full_grouped.csv"
PROCESSED_DATA_PATH = "data/processed/filtered.csv"

# ── Countries to keep
COUNTRIES_TO_KEEP = ['India', 'US', 'United Kingdom']

# ── Critical columns (nulls in these = row removal)
CRITICAL_COLUMNS = ['Date', 'Country/Region', 'Confirmed', 'Deaths', 'Recovered']


def filter_data():
    print("=" * 40)
    print("STEP 2: DATA FILTERING")
    print("=" * 40)

    # ── Load raw data from ingestion
    df = ingest_data()
    if df is None:
        print("ERROR: Could not load data from ingestion step")
        return None

    print("\n--- Before Filtering ---")
    print(f"  Shape: {df.shape[0]} rows, {df.shape[1]} columns")

    # ── Filter by country (only India, US, United Kingdom)
    df_filtered = df[df['Country/Region'].isin(COUNTRIES_TO_KEEP)].copy()
    print(f"\n✔ Country filter applied")
    print(f"  Rows after country filter: {df_filtered.shape[0]}")

    # ── Drop rows with nulls in critical columns
    df_filtered = df_filtered.dropna(subset=CRITICAL_COLUMNS)
    print(f"\n✔ Null values dropped from critical columns")
    print(f"  Rows after null removal: {df_filtered.shape[0]}")

    # ── Validate null values in critical columns
    print(f"\n--- Null Values Check (Critical Columns) ---")
    print(df_filtered[CRITICAL_COLUMNS].isnull().sum())

    # ── Summary by country
    print(f"\n--- Breakdown by Country ---")
    print(df_filtered['Country/Region'].value_counts())

    # ── Date range info
    print(f"\n--- Date Range ---")
    print(f"  Start: {df_filtered['Date'].min()}")
    print(f"  End:   {df_filtered['Date'].max()}")

    # ── Creates output directory if not exists
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)

    # ── Save filtered data
    df_filtered.to_csv(PROCESSED_DATA_PATH, index=False)
    print(f"\n✔ Filtered data saved to: {PROCESSED_DATA_PATH}")
    print(f"  Final shape: {df_filtered.shape[0]} rows, {df_filtered.shape[1]} columns")

    return df_filtered


if __name__ == "__main__":
    df_filtered = filter_data()
    if df_filtered is not None:
        print("\n✔ Filtering complete. Ready for transformation.")
