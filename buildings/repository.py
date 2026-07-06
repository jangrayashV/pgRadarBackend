from sqlalchemy.ext.asyncio import AsyncSession
from buildings.models import Building
from sqlalchemy import select
import uuid

class BuildingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_building(self, building_id: uuid.UUID) -> Building | None:
        result = await self.db.execute(select(Building).where(Building.id == building_id))
        return result.scalar_one_or_none()
    
    async def add_building(self, name: str, address: str, is_active: bool, owner_id: uuid.UUID, capacity: int) -> Building:
        new_building = Building(
            name=name,
            address=address,
            is_active=is_active,
            owner_id=owner_id,
            capacity=capacity
        )
        self.db.add(new_building)
        await self.db.commit()
        await self.db.refresh(new_building)
        return new_building
    
    async def update_building(self, building_id, name: str | None = None, address: str | None = None, is_active: bool | None = None, capacity: int | None = None ):
        building = await self.get_building(building_id)
        if name is not None:
            building.name = name 
        if address is not None:
            building.address = address
        if is_active is not None:   
            building.is_active = is_active
        if capacity is not None:
            building.capacity = capacity
        
        await self.db.commit()
        await self.db.refresh(building)
        return building