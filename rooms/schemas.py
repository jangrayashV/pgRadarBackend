from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class RoomBase(BaseModel):
    model_config = {"from_attributes": True}
 
 
class RoomCreateRequest(RoomBase):
    room_number: str | None = Field(default=None, max_length=50)
    capacity: int = Field(ge=1)
    rent_per_head: float = Field(gt=0)
 
 
class RoomResponse(RoomBase):
    id: uuid.UUID
    building_id: uuid.UUID
    room_number: str | None
    capacity: int
    rent_per_head: float
    created_at: datetime
 
 
class AssignTenantRequest(RoomBase):
    phone: str = Field(min_length=10, max_length=15)
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr | None = None
 
 
class AssignTenantResponse(RoomBase):
    message: str
    tenant_id: uuid.UUID
    room_id: uuid.UUID
    tenant_rent: float
    