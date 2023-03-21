from typing import List
from pydantic import BaseModel, Field


class Nutrition(BaseModel):
    weight: float

    fat: float
    saturated_fat: float
    carbohydrate: float
    fiber: float
    protein: float
    cholesterol: float

    energy_kcal: int
    protein_kcal: int
    fat_kcal: int
    carbohydrate_kcal: int


class Ingredient(BaseModel):
    name: str
    nutrition: Nutrition | None = Field(default=None)


class Recipe(BaseModel):
    id: str
    name: str
    category: List[str]
    area: List[str]
    instructions: str
    thumbnail: str | None
    video: str | None
    ingredients: List[Ingredient]

class RecipeSearch(BaseModel):
    id: str
    name: str
    thumbnail: str | None

class RecipeSearchCollection(BaseModel):
    recipes: List[RecipeSearch]
    total: int
