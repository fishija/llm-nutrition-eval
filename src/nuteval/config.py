from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

RAW_DATASET_PATH = RAW_DIR / "meals_dataset_v1.csv"
PROCESSED_DATASET_PATH = PROCESSED_DIR / "meals_dataset_v1.jsonl"
