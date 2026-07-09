from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class RentBase(BaseModel):
    model_config = {"from_attributes": True}
 

class RentEntryRequest(BaseModel):
    tenant_id: uuid.UUID
    room_id: uuid.UUID
    owner_id: uuid.UUID
    amount: float
    due_date: datetime
    paid_at: datetime | None = None
    
 
class RentEntryResponse(RentBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    room_id: uuid.UUID
    amount: float
    due_date: datetime
    paid_at: datetime | None
 
 
    
class TenantDuesResponse(RentBase):
    entries: list[RentEntryResponse]
    total_outstanding: float
 
 
class BuildingDuesResponse(RentBase):
    building_id: uuid.UUID
    total_outstanding: float
    entries: list[RentEntryResponse]
 
 