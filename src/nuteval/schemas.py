from pydantic import BaseModel, Field, computed_field
from typing import Optional
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


class MealEvaluationResponse(BaseModel):
    reasoning: str = Field(
        description="Step-by-step breakdown of ingredients, estimated weights, and macro calculations."
    )
    nutritional_values: NutritionalValues


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int

    @computed_field
    @property
    def total(self) -> int:
        return self.input_tokens + self.output_tokens


class CachedRun(BaseModel):
    meal_id: str
    run_idx: int
    model_name: str
    meal_evaluation_response: Optional[MealEvaluationResponse] = None
    token_usage: TokenUsage
    latency_s: float
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
