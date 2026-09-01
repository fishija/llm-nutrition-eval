from nuteval.schemas import ModelConfig, Provider
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "runs"

RAW_DATASET_PATH = RAW_DIR / "meals_dataset_v1.csv"
PROCESSED_DATASET_PATH = PROCESSED_DIR / "meals_dataset_v1.jsonl"

MODELS = {
    "claude-haiku-4-5-20251001": ModelConfig(
        name = "claude-haiku-4-5-20251001",
        provider=Provider.ANTHROPIC,
        input_price_per_m=1,
        output_price_per_m=5,
    ),
    "claude-sonnet-5": ModelConfig(
        name = "claude-sonnet-5",
        provider=Provider.ANTHROPIC,
        input_price_per_m=2,
        output_price_per_m=10,
    ),
    "gemini-3.7-flash": ModelConfig(
        name = "gemini-3.7-flash",
        provider=Provider.GOOGLE,
        input_price_per_m=0.75,
        output_price_per_m=3.75,
    ),
    "gemini-3.5-flash-lite": ModelConfig(
        name = "gemini-3.5-flash-lite",
        provider=Provider.GOOGLE,
        input_price_per_m=0.30,
        output_price_per_m=2.50,
    ),
}
