import uuid
from sqlalchemy import select, update
from rooms.models import Room, RoomUserAssociation
from sqlalchemy.ext.asyncio import AsyncSession
from rooms.schemas import RoomUpdate

class RoomRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_room_by_id(self, room_id: uuid.UUID) -> Room:
        result =  await self.session.execute(select(Room).where(Room.id == room_id))
        return result.scalar_one_or_none()
    
    async def create_room(self, number: int, capacity: bool, building_id: uuid.UUID, owner_id: uuid.UUID, vacancy: int, rent: int) -> Room:
        new_room = Room(
            number=number,
            capacity=capacity,
            building_id=building_id,
            owner_id=owner_id,
            vacancy=vacancy,
            rent=rent
        )
        self.session.add(new_room)
        await self.session.commit()
        return new_room
    
    async def update_room(self, room_id: str, updated_data: RoomUpdate):
        existing_room = await self.get_room_by_id(room_id)
        if updated_data.capacity != None:
            existing_room.capacity = updated_data.capacity
        if updated_data.vacancy != None:
            existing_room.vacancy = updated_data.vacancy
        if updated_data.rent != None:
            existing_room.rent = updated_data.rent
        
        await self.session.commit()
        await self.session.refresh(existing_room)
        return existing_room
            

    async def link_room_to_user(self, room_id: uuid.UUID, user_id: uuid.UUID, tenant_name, tenant_email, tenant_rent):
        new_association = RoomUserAssociation(room_id=room_id, user_id=user_id, tenant_name=tenant_name, tenant_email=tenant_email, tenant_rent=tenant_rent)
        self.session.add(new_association)
        await self.session.commit()
        return new_association
    
    async def update_room_association(self, link_id:str, tenant_rent: int, rent_paid: bool, rent_due: int):
        association = await self.session.execute(select(RoomUserAssociation).where(RoomUserAssociation.id == link_id))
        link = association.scalar_one_or_none()
        if tenant_rent!=None:
            link.tenant_rent = tenant_rent
        if rent_paid != None:
            link.rent_paid = rent_paid
        if rent_due != None:
            link.rent_due = rent_due
        
        await self.session.commit()
        await self.session.refresh(link)
        return link
    
    
    async def update_room_rent_per_head(self, room_id, new_rent):
        link = await self.session.execute(update(RoomUserAssociation).where(RoomUserAssociation.room_id==room_id).values(tenant_rent=new_rent))
        print(f"ROWS AFFECTED: {link.rowcount}")
        return link