from tqdm import tqdm

from nuteval.schemas import Provider, CachedRun, MealRecord, ModelConfig, TokenUsage
from nuteval.config import MODELS
from nuteval.cache import load_cached_runs, get_cached_runs_per_meal, append_cached_run
from nuteval.providers import evaluate_claude, evaluate_gemini
from nuteval.prompts import get_naive_evalutaion_prompt


def run_evaluation_for_model(model_name: str, meals: list[MealRecord], runs_per_meal: int = 3) -> list[CachedRun]:
    try:
        model_config: ModelConfig = MODELS[model_name]
    except KeyError:
        raise ValueError(f"Model {model_name} is not supported. Please choose one of these:\n {"\n".join([x for x in MODELS.keys()])}")

    cached_runs = load_cached_runs(model_name)
    results = cached_runs

    # build task queue with MealRecord and run_idx
    tasks_to_run: list[tuple[MealRecord, int]] = []
    for meal in meals:
        cached_runs_per_meal = get_cached_runs_per_meal(meal.id, cached_runs)
        cached_runs_count = len(cached_runs_per_meal)

        for run_idx in range(runs_per_meal - cached_runs_count):
            tasks_to_run.append((meal, run_idx + cached_runs_count))

    if not tasks_to_run:
        print(f"All {len(meals) * runs_per_meal} runs already cached for {model_name}.")
        return results

    print(f"Running {len(tasks_to_run)} API calls for {model_name}.")
    for meal, run_idx in tqdm(tasks_to_run, desc=model_name):
        prompt = get_naive_evalutaion_prompt(meal.description)

        match model_config.provider:
            case Provider.ANTHROPIC:
                evaluate_fn = evaluate_claude
            case Provider.GOOGLE:
                evaluate_fn = evaluate_gemini

        meal_eval_response = None
        latency_s = 0.0
        token_usage = TokenUsage(
            input_tokens=0,
            output_tokens=0
        )
        error_message = None

        try:
            meal_eval_response, latency_s, token_usage = evaluate_fn(model_name, prompt)
        except Exception as e:
            error_message = str(e)

        record = CachedRun(
            meal_id=meal.id,
            run_idx=run_idx,
            model_name=model_name,
            meal_evaluation_response=meal_eval_response,
            token_usage=token_usage,
            latency_s=latency_s,
            error_message=error_message
        )
        append_cached_run(record)
        results.append(record)

    return results
