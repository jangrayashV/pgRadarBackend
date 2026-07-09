from rent.repository import RentRepository
from rent.schemas import RentEntryRequest
from fastapi import Depends
import uuid as _uuid2
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from core.exceptions import NotFoundError, ForbiddenError
import logging

logger = logging.getLogger(__name__)

class RentService:
    def __init__(self, db: AsyncSession):
        self.repo = RentRepository(db)
        self.db = db
 
    async def create_entry(
        self,
        tenant_id: _uuid2.UUID,
        room_id: _uuid2.UUID,
        owner_id: _uuid2.UUID,
        amount: float,
        paid_at: datetime | None = None,
    ):
        """
        Create a rent entry. Called on tenant assignment and by scheduler monthly.
        due_date = now() at time of creation.
        """
        entry = await self.repo.create(
            tenant_id=tenant_id,
            room_id=room_id,
            owner_id=owner_id,
            amount=amount,
            due_date=datetime.now(timezone.utc),
            paid_at=paid_at,
        )
        logger.info("Rent entry created for tenant: %s amount: %s", tenant_id, amount)
        return entry
 
    async def mark_paid(self, entry_id: _uuid2.UUID, owner_id: _uuid2.UUID) -> None:
        entry = await self.repo.get_by_id(entry_id)
        if not entry:
            raise NotFoundError("Rent entry not found")
        if entry.owner_id != owner_id:
            raise ForbiddenError("You do not own this rent entry")
        if entry.paid_at is not None:
            raise ForbiddenError("Entry is already marked as paid")
        await self.repo.mark_paid(entry_id)
        logger.info("Rent entry %s marked paid by owner %s", entry_id, owner_id)
 
    async def get_my_dues(self, tenant_id: _uuid2.UUID) -> dict:
        entries = await self.repo.get_unpaid_by_tenant(tenant_id)
        total = sum(e.amount for e in entries)
        return {"entries": entries, "total_outstanding": total}
 
    async def get_building_dues(self, building_id: _uuid2.UUID, owner_id: _uuid2.UUID) -> dict:
        """Fetch all unpaid entries for all rooms in a building."""
        from rooms.repository import RoomRepository
        from buildings.repository import BuildingRepository
 
        building_repo = BuildingRepository(self.db)
        building = await building_repo.get_by_id(building_id)
        if not building:
            raise NotFoundError("Building not found")
        if building.owner_id != owner_id:
            raise ForbiddenError("You do not own this building")
 
        room_repo = RoomRepository(self.db)
        rooms = await room_repo.get_all_by_building(building_id)
 
        all_entries = []
        for room in rooms:
            entries = await self.repo.get_unpaid_by_room(room.id)
            all_entries.extend(entries)
 
        total = sum(e.amount for e in all_entries)
        return {
            "building_id": building_id,
            "total_outstanding": total,
            "entries": all_entries,
        }