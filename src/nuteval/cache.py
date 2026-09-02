from pathlib import Path

from nuteval.config import CACHE_DIR
from nuteval.schemas import CachedRun


def _get_cache_path(model: str, cache_dir: Path = CACHE_DIR) -> Path:
    """Change models name to filename safe and return cache path."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    safe_model_name = model.replace("/", "-").replace(":", "_")
    return cache_dir / f"{safe_model_name}.jsonl"


def load_cached_runs(model: str, cache_dir: Path = CACHE_DIR) -> list[CachedRun]:
    """Load all cached records for selected model."""
    records = []
    cache_path = _get_cache_path(model, cache_dir)

    if not cache_path.exists():
        return records

    with open(cache_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                record = CachedRun.model_validate_json(line)
                records.append(record)
            except Exception as e:
                print(f"Skipping cache line {line_num} in {cache_path}: {e}")

    return records


def append_cached_run(record: CachedRun, cache_dir: Path = CACHE_DIR):
    """Append record to the model's JSONL cache file."""
    model = record.model_name
    cache_file = _get_cache_path(model, cache_dir)
    with open(cache_file, "a", encoding="utf-8") as f:
        f.write(record.model_dump_json() + "\n")


def get_cached_runs_per_meal(meal_id: str, cached_runs: list[CachedRun]) -> list[CachedRun]:
    """Get all cached runs where meal_id matches."""
    return [cr for cr in cached_runs if cr.meal_id == meal_id]
