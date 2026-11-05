"""Load activity records for the educational prototype."""
from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "activity_logs.csv"
REQUIRED = {"timestamp", "user", "role", "event", "resource", "details"}

def load_activity(path=DATA_PATH):
    df = pd.read_csv(path)
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if df["timestamp"].isna().any():
        raise ValueError("Some timestamps could not be parsed.")
    return df.sort_values("timestamp").reset_index(drop=True)
