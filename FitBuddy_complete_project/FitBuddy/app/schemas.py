from typing import Literal
from pydantic import BaseModel, Field, ConfigDict

Goal = Literal["weight loss", "muscle gain", "general wellness", "flexibility"]
Intensity = Literal["low", "medium", "high"]

class UserInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    user_id: str = Field(min_length=2, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=0, le=500)
    goal: Goal
    intensity: Intensity

class FeedbackRequest(BaseModel):
    feedback: str = Field(min_length=3, max_length=2000)

class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: str
    name: str
    goal: str
    intensity: str
    workout_plan: str
    nutrition_tip: str
    updated: bool = False

class UserSummary(BaseModel):
    user_id: str
    name: str
    age: int
    weight: float
    goal: str
    intensity: str
    original_plan: str
    updated_plan: str | None = None
    feedback: str | None = None
