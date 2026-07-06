from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from rent.models import RentEntries
from sqlalchemy import select

class RentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def get_entry(self, entry_id):
        existing_entry = await self.db.execute(select(RentEntries).where(RentEntries.id == entry_id))
        entry = existing_entry.scalar_one_or_none()
        return entry
    
    async def get_unpaid_entries(self, tenant_id):
        result = await self.db.execute(
            select(RentEntries).where(
                RentEntries.tenant_id == tenant_id,
                RentEntries.paid_at.is_(None)
            )
        )
        return result.scalars().all()   
    
    async def add_rent_entry(self, tenant_id, room_id, owner_id, rent, paid_at):
        new_entry = RentEntries(
            tenant_id=tenant_id,
            room_id=room_id,
            owner_id=owner_id,
            rent=rent,
            paid_at=paid_at
        )
        
        self.db.add(new_entry)
        await self.db.commit()
        await self.db.refresh(new_entry)
        return new_entry
    
    async def mark_paid(self, entry_id):
        existing_entry = await self.get_entry(entry_id)
        
        existing_entry.paid_at = datetime.now(timezone.utc)
        
        await self.db.flush()
        await self.db.refresh(existing_entry)
        return existing_entry
        
