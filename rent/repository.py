from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from rent.models import RentEntry
from sqlalchemy import select, update
import uuid as _uuid


class RentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def create(
        self,
        tenant_id: _uuid.UUID,
        room_id: _uuid.UUID,
        owner_id: _uuid.UUID,
        amount: float,
        due_date: datetime,
        paid_at: datetime | None = None,
    ) -> RentEntry:
        entry = RentEntry(
            tenant_id=tenant_id,
            room_id=room_id,
            owner_id=owner_id,
            amount=amount,
            due_date=due_date,
            paid_at=paid_at,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry
 
    async def get_by_id(self, entry_id: _uuid.UUID) -> RentEntry | None:
        result = await self.db.execute(select(RentEntry).where(RentEntry.id == entry_id))
        return result.scalar_one_or_none()
 
    async def get_unpaid_by_tenant(self, tenant_id: _uuid.UUID) -> list[RentEntry]:
        result = await self.db.execute(
            select(RentEntry).where(
                RentEntry.tenant_id == tenant_id,
                RentEntry.paid_at.is_(None),
            ).order_by(RentEntry.due_date.asc())
        )
        return list(result.scalars().all())
 
    async def get_unpaid_by_room(self, room_id: _uuid.UUID) -> list[RentEntry]:
        result = await self.db.execute(
            select(RentEntry).where(
                RentEntry.room_id == room_id,
                RentEntry.paid_at.is_(None),
            )
        )
        return list(result.scalars().all())
 
    async def mark_paid(self, entry_id: _uuid.UUID) -> None:
        await self.db.execute(
            update(RentEntry)
            .where(RentEntry.id == entry_id)
            .values(paid_at=datetime.now(timezone.utc))
        )
 
 