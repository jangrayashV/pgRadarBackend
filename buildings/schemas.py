from pydantic import BaseModel, Field
from typing import Optional

class BuildingCreate(BaseModel):
    name: str = Field(..., example="Sunset Apartments")
    address: str = Field(..., example="123 Main St, Springfield")
    is_active: bool = Field(..., example=True)
    capacity: int = Field(..., example=100)
    rent: int = Field(..., example=10000)

class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None 
    capacity: Optional[int] = None
    rent: Optional[int] = None