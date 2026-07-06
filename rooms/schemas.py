from pydantic import BaseModel, Field
from typing import Optional

class RoomCreate(BaseModel):
    number: int = Field(..., description="The room number")
    capacity: int = Field(..., description="Indicates the sharing capacity of the room")
    building_id: str = Field(..., description="The unique identifier of the building where the room is located")
    vacancy: int = Field(..., description="The number of vacant spots in the room")
    rent: int = Field(..., description="The amount of rent")

class RoomUpdate(BaseModel):
    capacity: Optional[int] = None
    vacancy: Optional[int] = None
    rent: Optional[int] = None