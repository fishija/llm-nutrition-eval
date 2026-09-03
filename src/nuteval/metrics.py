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


def compute_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-model summary: calories accuracy, mean cost, mean latency, and error rate."""
    n_runs = df.groupby("model_name").size().rename("n_runs")
    n_errors = df.groupby("model_name")["has_error"].sum().rename("n_errors")
    error_rate = (n_errors / n_runs * 100).rename("error_rate_pct")

    # Accuracy based on calories APE only (excludes error/zero-gt rows automatically, since ape is NaN there)
    calories_mape = df.groupby("model_name")["calories_ape"].mean().rename("calories_mape")
    accuracy_pct = (100 - calories_mape).clip(lower=0).rename("calories_accuracy_pct")

    mean_cost = df.groupby("model_name")["cost_usd"].mean().rename("mean_cost_usd")
    mean_latency = df.groupby("model_name")["latency_s"].mean().rename("mean_latency_s")

    summary = pd.concat(
        [accuracy_pct, calories_mape, mean_cost, mean_latency, error_rate],
        axis=1,
    ).reset_index()

    return summary.sort_values("calories_accuracy_pct", ascending=False).reset_index(drop=True)


def format_summary_for_display(summary_df: pd.DataFrame) -> pd.DataFrame:
    """Round summary columns for display."""
    out = summary_df.copy()
    out["calories_accuracy_pct"] = out["calories_accuracy_pct"].round(1)
    out["calories_mape"] = out["calories_mape"].round(1)
    out["mean_cost_usd"] = out["mean_cost_usd"].round(4)
    out["mean_latency_s"] = out["mean_latency_s"].round(3)
    return out
