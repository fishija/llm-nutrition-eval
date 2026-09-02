import pandas as pd
from nuteval.config import MODELS
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
                # Ground truth
                "gt_calories": meal.ground_truth.calories,
                "gt_protein": meal.ground_truth.protein_g,
                "gt_carbs": meal.ground_truth.carbs_g,
                "gt_fat": meal.ground_truth.fat_g,
            }

            if not has_error and run.meal_evaluation_response is not None:
                pred = run.meal_evaluation_response.nutritional_values
                row.update({
                    "pred_calories": pred.calories,
                    "pred_protein": pred.protein_g,
                    "pred_carbs": pred.carbs_g,
                    "pred_fat": pred.fat_g,
                    # Absolute errors
                    "cal_mae": abs(pred.calories - meal.ground_truth.calories),
                    "protein_mae": abs(pred.protein_g - meal.ground_truth.protein_g),
                    "carbs_mae": abs(pred.carbs_g - meal.ground_truth.carbs_g),
                    "fat_mae": abs(pred.fat_g - meal.ground_truth.fat_g),
                })
            rows.append(row)

    return pd.DataFrame(rows)
