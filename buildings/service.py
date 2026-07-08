from buildings.repository import BuildingRepository
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import uuid as uuid_module
from core.exceptions import NotFoundError, ForbiddenError

logger = logging.getLogger(__name__)
 
 
class BuildingService:
    def __init__(self, db: AsyncSession):
        self.repo = BuildingRepository(db)
 
    async def _get_owned_building(self, building_id: uuid_module.UUID, owner_id: uuid_module.UUID):
        """Fetch building and verify ownership. Raises if not found or not owned."""
        building = await self.repo.get_by_id(building_id)
        if not building:
            raise NotFoundError("Building not found")
        if building.owner_id != owner_id:
            raise ForbiddenError("You do not own this building")
        return building
 
    async def create(
        self,
        owner_id: uuid_module.UUID,
        name: str,
        address: str,
        city: str,
        state: str,
    ):
        building = await self.repo.create(owner_id=owner_id, name=name, address=address, city=city, state=state)
        logger.info("Building created: %s by owner: %s", building.id, owner_id)
        return building
 
    async def get_all(self, owner_id: uuid_module.UUID) -> list:
        return await self.repo.get_all_by_owner(owner_id)
 
    async def get_one(self, building_id: uuid_module.UUID, owner_id: uuid_module.UUID):
        return await self._get_owned_building(building_id, owner_id)
 
    async def update(
        self,
        building_id: uuid_module.UUID,
        owner_id: uuid_module.UUID,
        name: str | None = None,
        address: str | None = None,
        city: str | None = None,
        state: str | None = None,
    ):
        building = await self._get_owned_building(building_id, owner_id)
        await self.repo.update(building_id, name=name, address=address, city=city, state=state)
        return building
 
    async def delete(self, building_id: uuid_module.UUID, owner_id: uuid_module.UUID) -> None:
        await self._get_owned_building(building_id, owner_id)
        await self.repo.delete(building_id)
        logger.info("Building deleted: %s", building_id)
 
 