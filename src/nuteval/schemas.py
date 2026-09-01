from pydantic import BaseModel, Field, computed_field
from datetime import datetime, timezone
from enum import Enum


class Quantity(str, Enum):
    EXPLICIT = "explicit"
    VAGUE = "vague"


class Complexity(str, Enum):
    SIMPLE = "simple"
    COMPOSITE = "composite"
    COMPLEX = "complex"


class Naming(str, Enum):
    GENERIC = "generic"
    BRANDED = "branded"


class Tags(BaseModel):
    quantity: Quantity
    complexity: Complexity
    naming: Naming


class Ingredient(BaseModel):
    name: str
    amount_g: float


class NutritionalValues(BaseModel):
    calories: float = Field(description="Total energy in kcal")
    protein_g: float = Field(description="Total protein in grams")
    carbs_g: float = Field(description="Total carbohydrates in grams")
    fat_g: float = Field(description="Total fat in grams")


class MealRecord(BaseModel):
    id: str = Field(examples=["meal_001", "meal_099"])
    description: str
    ground_truth: NutritionalValues
    tags: Tags
    ingredients: list[Ingredient]
    notes: str = ""
