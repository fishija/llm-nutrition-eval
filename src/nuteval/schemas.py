from pydantic import BaseModel, Field
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


class GroundTruth(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class Tags(BaseModel):
    quantity: Quantity
    complexity: Complexity
    naming: Naming


class Ingredient(BaseModel):
    name: str
    amount_g: float


class MealRecord(BaseModel):
    id: str = Field(examples=["meal_001", "meal_099"])
    description: str
    ground_truth: GroundTruth
    tags: Tags
    ingredients: list[Ingredient]
    notes: str = ""
