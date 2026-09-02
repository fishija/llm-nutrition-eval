NAIVE_PROMPT = """\
Analyze the following meal description and estimate its nutritional values:

Meal:
{description}

Instructions:
1. In the reasoning field, break down the meal into estimated ingredients and weights in grams, calculating calories and macronutrients step-by-step.
2. For vague portions, assume standard average serving sizes.
3. Fill in the total nutritional values based on your calculation.
"""


def get_naive_evalutaion_prompt(description: str):
    return NAIVE_PROMPT.format(description=description.strip())
