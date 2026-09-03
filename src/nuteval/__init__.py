from nuteval.dataset import csv_to_jsonl, load_dataset
from nuteval.cache import load_cached_runs, append_cached_run, get_cached_runs_per_meal
from nuteval.evaluation import run_evaluation_for_model
from nuteval.metrics import build_evaluation_dataframe, add_error_metrics
from nuteval.plots import plot_mean_ape_per_model_and_nutrient, plot_error_distribution_per_model
from nuteval.schemas import CachedRun
from nuteval.config import MODELS


__all__ = [
    "MODELS",
    "CachedRun",
    "csv_to_jsonl",
    "load_dataset",
    "load_cached_runs",
    "append_cached_run",
    "get_cached_runs_per_meal",
    "run_evaluation_for_model",
    "build_evaluation_dataframe",
    "add_error_metrics",
    "plot_mean_ape_per_model_and_nutrient",
    "plot_error_distribution_per_model",
]
