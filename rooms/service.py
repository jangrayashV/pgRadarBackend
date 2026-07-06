from rooms.repository import RoomRepository
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from fastapi import Depends, HTTPException
from rooms.schemas import RoomCreate, RoomUpdate
from auth.models import User
from core.dependencies import get_owner
from auth.service import AuthService
from auth.schemas import RegisterRequest
from rent.schemas import RentEntryRequest
from rent.service import RentService


class RoomService:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.room_repository = RoomRepository(db)
        self.auth_service = AuthService(db)
        self.rent_service = RentService(db)

    async def get_room(self, room_id: str):
        return await self.room_repository.get_room_by_id(room_id)

    async def create_room(self, data: RoomCreate,  owner: User = Depends(get_owner)):
        return await self.room_repository.create_room(
            number=data.number,
            capacity=data.capacity,
            building_id=data.building_id,
            owner_id=owner.id,
            vacancy=data.vacancy,
            rent=data.rent
        )

    async def link_room_to_user(self, room_id: str, user: RegisterRequest, owner: User = Depends(get_owner)):
        print(type(user))
        existing_room = await self.room_repository.get_room_by_id(room_id)
        if not existing_room:
            raise HTTPException(404, detail="room doesn't exist")
        
        if existing_room.vacancy == 0:
            raise HTTPException(404, detail="room is full")
        
        if user.role != "tenant":
            return HTTPException(404, detail="user must be tenant")
        new_tenant = await self.auth_service.register(user)
        
        room_rent = existing_room.rent
        room_vacancy = existing_room.vacancy
        room_capacity = existing_room.capacity
        tenant_rent = room_rent / ((room_capacity - room_vacancy)+1)
        
        
        new_link = await self.room_repository.link_room_to_user(room_id, new_tenant.id, new_tenant.full_name, new_tenant.email, tenant_rent)
        
        updated_data = RoomUpdate(vacancy=existing_room.vacancy-1)
        
        updated_room = await self.room_repository.update_room(room_id=existing_room.id, updated_data=updated_data)
        
        updated_rent_per_head = await self.room_repository.update_room_rent_per_head(room_id=room_id, new_rent=tenant_rent)
        
        rent_entry_data = RentEntryRequest(
            owner_id=owner.id,
            tenant_id=new_tenant.id,
            room_id=room_id,
            rent=tenant_rent
        )
        new_rent_entry = await self.rent_service.add_entry(rent_entry_data, owner=owner)
        
        return new_link