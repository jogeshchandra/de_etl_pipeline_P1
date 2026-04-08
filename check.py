import pandas as pd

RAW_DATA_PATH = "data/raw/full_grouped.csv"

def check_data():
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Data loaded from {RAW_DATA_PATH}")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    return df

if __name__ == "__main__":
    df = check_data()