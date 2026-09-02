import time

from nuteval.schemas import MealEvaluationResponse, TokenUsage


def evaluate_claude(model_name: str, prompt: str) -> tuple[MealEvaluationResponse, float, TokenUsage]:
    """Evaluate meal nutritional values using Anthropic Claude."""
    try:
        import anthropic
    except ImportError:
        raise ImportError(
            "The 'anthropic' package is required."
        )

    client = anthropic.Anthropic()

    start = time.perf_counter()
    response = client.messages.parse(
        model=model_name,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        output_format=MealEvaluationResponse
    )
    meal_eval_response = response.parsed_output
    latency = round(time.perf_counter() - start, 3)
    usage = TokenUsage(
        input_tokens=response.usage.input_tokens or 0,
        output_tokens=response.usage.output_tokens or 0
    )
    return meal_eval_response, latency, usage


def evaluate_gemini(model_name: str, prompt: str):
    """Evaluate meal nutritional values using Google gemini."""
    try:
        from google import genai
    except ImportError:
        raise ImportError(
            "The 'google-genai' package is required."
        )

    client = genai.Client()

    start = time.perf_counter()
    response = client.interactions.create(
        model=model_name,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": MealEvaluationResponse.model_json_schema()
        }
    )
    meal_eval_response = MealEvaluationResponse.model_validate_json(response.output_text)
    latency = round(time.perf_counter() - start, 3)
    usage = TokenUsage(
        input_tokens=response.usage.total_input_tokens or 0,
        output_tokens=response.usage.total_output_tokens or 0
    )
    return meal_eval_response, latency, usage
