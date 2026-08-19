from pydantic import BaseModel
from typing import Optional


class WeightCategoryCreate(BaseModel):
    categoryName: str
    minWeight: float
    maxWeight: Optional[float] = None


class WeightCategory(BaseModel):
    weightCategoryId: str
    categoryName: str
    minWeight: float
    maxWeight: Optional[float] = None
    isActive: bool = True
