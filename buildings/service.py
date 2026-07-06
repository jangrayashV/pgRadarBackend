from buildings.schemas import BuildingCreate, BuildingUpdate
from core.dependencies import get_owner
from fastapi import Depends, HTTPException
from buildings.repository import BuildingRepository
from sqlalchemy.ext.asyncio import AsyncSession
from auth.models import User

class BuildingService:
    def __init__(self, db: AsyncSession):
        self.repo = BuildingRepository(db)

    async def create_building(self, building_data:BuildingCreate, owner: User = Depends(get_owner)):
        new_building = await self.repo.add_building(name=building_data.name, address=building_data.address, is_active=building_data.is_active, owner_id=owner.id, capacity=building_data.capacity)
        return new_building
        

    async def get_building(self, building_id):
        building = await self.repo.get_building(building_id)
        if not building:
            raise HTTPException(404, detail="building doesn't exist")
        return building

    async def update_building(self, building_id, building_data: BuildingUpdate):
        building = await self.repo.get_building(building_id)
        if not building:
            raise HTTPException(404, detail="building doesn't exist")
        new_update = await self.repo.update_building(building_id, building_data)
        return new_update

    async def delete_building(self, building_id):
        # Logic to delete a building from the database
        pass