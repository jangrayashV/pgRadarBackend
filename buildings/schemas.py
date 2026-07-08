from pydantic import BaseModel, Field  
import uuid
from datetime import datetime

class BuildingBase(BaseModel):
    model_config = {"from_attributes": True}
 
 
class BuildingCreateRequest(BuildingBase):
    name: str = Field(min_length=1, max_length=255)
    address: str = Field(min_length=1, max_length=500)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
 
 
class BuildingUpdateRequest(BuildingBase):
    name: str | None = Field(default=None, max_length=255)
    address: str | None = Field(default=None, max_length=500)
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=100)
 
 
class BuildingResponse(BuildingBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    address: str
    city: str
    state: str
    created_at: datetime
 