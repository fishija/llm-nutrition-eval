import pandas as pd
from nuteval.config import MODELS, NUTRIENT_FIELDS
from nuteval.schemas import CachedRun, MealRecord


def build_evaluation_dataframe(
    meals: list[MealRecord],
    all_runs: dict[str, list[CachedRun]],
) -> pd.DataFrame:
    """Flatten cached model runs and join with ground truth into an analysis DataFrame."""
    rows = []
    meal_map = {m.id: m for m in meals}

    for model_name, runs in all_runs.items():
        cfg = MODELS[model_name]
        for run in runs:
            meal = meal_map[run.meal_id]
            has_error = run.error_message is not None or run.meal_evaluation_response is None

            row = {
                "model_name": model_name,
                "meal_id": run.meal_id,
                "run_idx": run.run_idx,
                "latency_s": run.latency_s,
                "input_tokens": run.token_usage.input_tokens,
                "output_tokens": run.token_usage.output_tokens,
                "total_tokens": run.token_usage.total,
                "cost_usd": cfg.calculate_cost(run.token_usage.input_tokens, run.token_usage.output_tokens),
                "has_error": has_error,
                "error_message": run.error_message,
                # Tags
                "quantity": meal.tags.quantity.value,
                "complexity": meal.tags.complexity.value,
                "naming": meal.tags.naming.value,
            }

            # Ground truth
            for short_name, attr in NUTRIENT_FIELDS.items():
                row[f"gt_{short_name}"] = getattr(meal.ground_truth, attr)

            # Predictions
            if not has_error and run.meal_evaluation_response is not None:
                pred = run.meal_evaluation_response.nutritional_values
                for short_name, attr in NUTRIENT_FIELDS.items():
                    row[f"pred_{short_name}"] = getattr(pred, attr)

            rows.append(row)

    return pd.DataFrame(rows)


def add_error_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add MAE, signed % error and absolute % error for each nutrient."""
    for n in NUTRIENT_FIELDS:
        # If row has_error, the values will be NaN
        gt = df[f"gt_{n}"]
        pred = df[f"pred_{n}"]
        err = pred - gt

        df[f"{n}_mae"] = err.abs()
        df[f"{n}_pct_err"] = (err / gt * 100).where(gt != 0)
        df[f"{n}_ape"] = df[f"{n}_pct_err"].abs()

    return df
