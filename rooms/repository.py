import uuid as _uuid
from sqlalchemy import select, update  
from sqlalchemy.ext.asyncio import AsyncSession  
from rooms.models import Room, RoomUserAssociation  
 
 
class RoomRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def get_by_id(self, room_id: _uuid.UUID) -> Room | None:
        result = await self.db.execute(select(Room).where(Room.id == room_id))
        return result.scalar_one_or_none()
 
    async def get_all_by_building(self, building_id: _uuid.UUID) -> list[Room]:
        result = await self.db.execute(select(Room).where(Room.building_id == building_id))
        return list(result.scalars().all())
 
    async def create(
        self,
        building_id: _uuid.UUID,
        capacity: int,
        rent_per_head: float,
        room_number: str | None = None,
    ) -> Room:
        room = Room(building_id=building_id, capacity=capacity, rent_per_head=rent_per_head, room_number=room_number)
        self.db.add(room)
        await self.db.flush()
        return room
 
    async def get_active_associations(self, room_id: _uuid.UUID) -> list[RoomUserAssociation]:
        result = await self.db.execute(
            select(RoomUserAssociation).where(
                RoomUserAssociation.room_id == room_id,
                RoomUserAssociation.vacated_at.is_(None),
            )
        )
        return list(result.scalars().all())
 
    async def create_association(
        self,
        room_id: _uuid.UUID,
        tenant_id: _uuid.UUID,
        tenant_rent: float,
    ) -> RoomUserAssociation:
        assoc = RoomUserAssociation(room_id=room_id, tenant_id=tenant_id, tenant_rent=tenant_rent)
        self.db.add(assoc)
        await self.db.flush()
        return assoc
 
    async def update_all_tenant_rents(self, room_id: _uuid.UUID, new_rent: float) -> None:
        """Update rent for all active tenants in a room after new tenant joins."""
        await self.db.execute(
            update(RoomUserAssociation)
            .where(
                RoomUserAssociation.room_id == room_id,
                RoomUserAssociation.vacated_at.is_(None),
            )
            .values(tenant_rent=new_rent)
        )
 
    async def vacate_tenant(self, room_id: _uuid.UUID, tenant_id: _uuid.UUID) -> None:
        from datetime import datetime, timezone
        await self.db.execute(
            update(RoomUserAssociation)
            .where(
                RoomUserAssociation.room_id == room_id,
                RoomUserAssociation.tenant_id == tenant_id,
                RoomUserAssociation.vacated_at.is_(None),
            )
            .values(vacated_at=datetime.now(timezone.utc))
        )
 