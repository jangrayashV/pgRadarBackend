from sqlalchemy.ext.asyncio import AsyncSession
from buildings.models import Building
from sqlalchemy import select, update, delete
import uuid


class BuildingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def get_by_id(self, building_id: uuid.UUID) -> Building | None:
        result = await self.db.execute(select(Building).where(Building.id == building_id))
        return result.scalar_one_or_none()
 
    async def get_all_by_owner(self, owner_id: uuid.UUID) -> list[Building]:
        result = await self.db.execute(select(Building).where(Building.owner_id == owner_id))
        return list(result.scalars().all())
 
    async def create(
        self,
        owner_id: uuid.UUID,
        name: str,
        address: str,
        city: str,
        state: str,
    ) -> Building:
        building = Building(owner_id=owner_id, name=name, address=address, city=city, state=state)
        self.db.add(building)
        await self.db.flush()
        return building
 
    async def update(self, building_id: uuid.UUID, **kwargs) -> None:
        filtered = {k: v for k, v in kwargs.items() if v is not None}
        if not filtered:
            return
        await self.db.execute(
            update(Building).where(Building.id == building_id).values(**filtered)
        )
 
    async def delete(self, building_id: uuid.UUID) -> None:
        await self.db.execute(delete(Building).where(Building.id == building_id))
 
 