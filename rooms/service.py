from rooms.repository import RoomRepository
from buildings.service import BuildingService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from rooms.schemas import RoomCreate, RoomUpdate
from auth.models import User
from core.dependencies import get_owner
from auth.service import AuthService
from auth.schemas import RegisterRequest
from rent.schemas import RentEntryRequest
import logging
from core.exceptions import NotFoundError, ForbiddenError, ValidationError
import uuid

logger = logging.getLogger(__name__)
 
 
class RoomService:
    def __init__(self, db: AsyncSession):
        self.repo = RoomRepository(db)
        # self.building_repo = BuildingRepository(db)
        self.building_service = BuildingService(db)
        self.auth_service = AuthService(db)
 
    # async def _verify_building_ownership(self, building_id: uuid.UUID, owner_id: uuid.UUID):
    #     building = await self.building_repo.get_by_id(building_id)
    #     if not building:
    #         raise NotFoundError("Building not found")
    #     if building.owner_id != owner_id:
    #         raise ForbiddenError("You do not own this building")
    #     return building
 
    async def _verify_room_ownership(self, room_id: uuid.UUID, owner_id: uuid.UUID):
        room = await self.repo.get_by_id(room_id)
        if not room:
            raise NotFoundError("Room not found")
        await self.building_service._get_owned_building(room.building_id, owner_id)
        return room
 
    async def create_room(
        self,
        building_id: uuid.UUID,
        owner_id: uuid.UUID,
        capacity: int,
        rent_per_head: float,
        room_number: str | None = None,
    ):
        await self._verify_building_ownership(building_id, owner_id)
        room = await self.repo.create(
            building_id=building_id,
            capacity=capacity,
            rent_per_head=rent_per_head,
            room_number=room_number,
        )
        logger.info("Room created: %s in building: %s", room.id, building_id)
        return room
 
    async def get_rooms(self, building_id: uuid.UUID, owner_id: uuid.UUID) -> list:
        await self._verify_building_ownership(building_id, owner_id)
        return await self.repo.get_all_by_building(building_id)
 
    async def assign_tenant(
        self,
        room_id: uuid.UUID,
        owner_id: uuid.UUID,
        phone: str,
        full_name: str,
        email: str | None = None,
    ) -> tuple:
        """
        Creates tenant user, assigns to room, splits rent, creates first rent entry.
        Returns (association, temp_password).
        """
        # lazy import to avoid circular
        from rent.service import RentService
 
        room = await self._verify_room_ownership(room_id, owner_id)
 
        # check vacancy
        active_associations = await self.repo.get_active_associations(room_id)
        if len(active_associations) >= room.capacity:
            raise ValidationError("Room is at full capacity")
 
        # create tenant user via auth service
        tenant = await self.auth_service.create_tenant(
            phone=phone,
            full_name=full_name,
            email=email,
        )
 
        # calculate new rent per head after this tenant joins
        new_occupant_count = len(active_associations) + 1
        new_rent_per_head = room.rent_per_head / new_occupant_count
 
        # update existing tenants' rent
        if active_associations:
            await self.repo.update_all_tenant_rents(room_id, new_rent_per_head)
 
        # create association for new tenant
        assoc = await self.repo.create_association(
            room_id=room_id,
            tenant_id=tenant.id,
            tenant_rent=new_rent_per_head,
        )
 
        # create first rent entry
        rent_service = RentService(self.db if hasattr(self, 'db') else None)
        await rent_service.create_entry(
            tenant_id=tenant.id,
            room_id=room_id,
            owner_id=owner_id,
            amount=new_rent_per_head,
        )
 
        logger.info("Tenant %s assigned to room %s", tenant.id, room_id)
        return assoc
 
    async def vacate_tenant(
        self,
        room_id: uuid.UUID,
        tenant_id: uuid.UUID,
        owner_id: uuid.UUID,
    ) -> None:
        room = await self._verify_room_ownership(room_id, owner_id)
        await self.repo.vacate_tenant(room_id, tenant_id)
 
        # recalculate rent for remaining tenants
        remaining = await self.repo.get_active_associations(room_id)
        if remaining:
            new_rent = room.rent_per_head / len(remaining)
            await self.repo.update_all_tenant_rents(room_id, new_rent)
 
        logger.info("Tenant %s vacated room %s", tenant_id, room_id)
 
 


    # async def link_room_to_user(self, room_id: str, user: RegisterRequest, owner: User = Depends(get_owner)):
    #     print(type(user))
    #     existing_room = await self.room_repository.get_room_by_id(room_id)
        # if not existing_room:
        #     raise HTTPException(404, detail="room doesn't exist")
        
        # if existing_room.vacancy == 0:
        #     raise HTTPException(404, detail="room is full")
        
        # if user.role != "tenant":
        #     return HTTPException(404, detail="user must be tenant")
        # new_tenant = await self.auth_service.register(user)
        
        # room_rent = existing_room.rent
        # room_vacancy = existing_room.vacancy
        # room_capacity = existing_room.capacity
        # tenant_rent = room_rent / ((room_capacity - room_vacancy)+1)
        
        
        # new_link = await self.room_repository.link_room_to_user(room_id, new_tenant.id, new_tenant.full_name, new_tenant.email, tenant_rent)
        
        # updated_data = RoomUpdate(vacancy=existing_room.vacancy-1)
        
        # updated_room = await self.room_repository.update_room(room_id=existing_room.id, updated_data=updated_data)
        
        # updated_rent_per_head = await self.room_repository.update_room_rent_per_head(room_id=room_id, new_rent=tenant_rent)
        
        # rent_entry_data = RentEntryRequest(
        #     owner_id=owner.id,
        #     tenant_id=new_tenant.id,
        #     room_id=room_id,
        #     rent=tenant_rent
        # )
        # new_rent_entry = await self.rent_service.add_entry(rent_entry_data, owner=owner)
        
        # return new_link