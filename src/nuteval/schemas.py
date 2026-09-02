from pydantic import BaseModel, Field, computed_field
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timezone
from enum import Enum


class Provider(str, Enum):
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


@dataclass(frozen=True)
class ModelConfig:
    name: str
    provider: Provider
    # prices per 1m tokens (USD)
    input_price_per_m: float
    output_price_per_m: float

    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate total USD cost for a run."""
        input_cost = (input_tokens / 1_000_000) * self.input_price_per_m
        output_cost = (output_tokens / 1_000_000) * self.output_price_per_m
        return round(input_cost + output_cost, 6)


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
