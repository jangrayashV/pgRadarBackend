from rent.repository import RentRepository
from auth.service import AuthService 
from auth.repository import AuthRepository
from fastapi import HTTPException
from rent.schemas import RentEntryRequest
from core.dependencies import get_owner, get_tenant
from fastapi import Depends
from auth.models import User

class RentService:
    def __init__(self, db):
        self.rent_session = RentRepository(db)
        self.auth_session = AuthRepository(db)
        
    async def add_entry(self, entry_data: RentEntryRequest, owner: User = Depends(get_owner)):
        existing_tenant = await self.auth_session.get_user_by_id(entry_data.tenant_id)
        if not existing_tenant:
            raise HTTPException(404, detail="tenant doesn't exist")
        
        new_entry = await self.rent_session.add_rent_entry(tenant_id=entry_data.tenant_id, owner_id=owner.id, rent=entry_data.rent,room_id= entry_data.room_id, paid_at=entry_data.paid_at)
        
        return new_entry
    
    async def mark_paid(self, entry_id, owner: User = Depends(get_owner)):
        existing_entry = await self.rent_session.get_entry(entry_id)
        if not existing_entry:
            raise HTTPException(404, detail="Entry doesn't exist")
        
        mark_entry = await self.rent_session.mark_paid(entry_id)
        
        return mark_entry

    async def get_my_dues(self, tenant: User = Depends(get_tenant)):
        entries = await self.rent_session.get_unpaid_entries(tenant.id)
        
        total = sum(entry.rent for entry in entries)
        return {
            "entries": entries,
            "total_outstanding": total
        }

    async def get_unpaid_dues(self,tenant_id, owner: User = Depends(get_owner)):
        entries = await self.rent_session.get_unpaid_entries(tenant_id)
        
        total = sum(entry.rent for entry in entries)
        return {
            "entries": entries,
            "total_outstanding": total
        }