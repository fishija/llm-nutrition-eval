from pathlib import Path
import csv

from nuteval.schemas import MealRecord, NutritionalValues, Ingredient, Tags
from nuteval.config import RAW_DATASET_PATH, PROCESSED_DATASET_PATH


def _str_to_float(s: str) -> float:
    """Convert str to float. Works with '.' and ',' as delimiter."""
    s = s.replace(",", ".")
    return float(s)


def _parse_ingredients(ingredients: str) -> list[Ingredient]:
    """Parse list of ingredients."""
    ingredient_list = ingredients.split(';')

    # separate str,float pairs per ingredient
    for i in range(len(ingredient_list)):
        ingredient = ingredient_list[i]
        temp_ingredient = ingredient.split(',', 1)
        ingredient_list[i] = Ingredient(
            name = str(temp_ingredient[0]),
            amount_g = _str_to_float(temp_ingredient[1])
        )

    return ingredient_list


def _row_to_record(row: dict) -> MealRecord:
    """Convert csv row to MealRecord."""
    return MealRecord(
        id = row["id"],
        description = row["description"],
        ground_truth = NutritionalValues(
            calories = _str_to_float(row["calories"]),
            protein_g = _str_to_float(row["protein_g"]),
            carbs_g = _str_to_float(row["carbs_g"]),
            fat_g = _str_to_float(row["fat_g"]),
                                     
        ),
        tags = Tags(
            quantity = row["quantity"],
            complexity = row["complexity"],
            naming = row["naming"]
        ),
        ingredients = _parse_ingredients(str(row["ingredients"])),
        notes = row.get("notes", "")
    )


def csv_to_jsonl(csv_path: Path = RAW_DATASET_PATH, jsonl_path: Path = PROCESSED_DATASET_PATH) -> list[MealRecord]:
    """Convert dataset .csv to .jsonl with cleaned values."""
    meal_records = []
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                meal_records.append(_row_to_record(row))
            except Exception as e:
                print(f"Skipping {row.get('id')}: {e}")

    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for mr in meal_records:
            f.write(mr.model_dump_json() + "\n")

    print(f"Wrote {len(meal_records)} records to {jsonl_path}")
    return meal_records


def load_dataset(jsonl_path: Path = PROCESSED_DATASET_PATH) -> list[MealRecord]:
    """Load processed .jsonl dataset into list of MealRecord objects."""
    meal_records = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                meal_records.append(MealRecord.model_validate_json(line))
            except Exception as e:
                print(f"Skipping line {line_num}: {e}")
    print(f"Read {len(meal_records)} records from {jsonl_path}")
    return meal_records
