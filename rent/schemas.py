from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class RentEntryRequest(BaseModel):
    tenant_id: uuid.UUID
    room_id: uuid.UUID
    owner_id: uuid.UUID
    rent: float
    paid_at: datetime | None = None