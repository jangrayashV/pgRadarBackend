from fastapi import APIRouter, Depends, HTTPException
from core.dependencies import require_owner
from rooms.schemas import RoomCreateRequest
from rooms.service import RoomService
from auth.models import User
from core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from auth.schemas import RegisterRequest


router = APIRouter()

@router.post("/rooms")
async def create_room(room_data: RoomCreateRequest,db: AsyncSession = Depends(get_db),  owner: User = Depends(require_owner)):
    room_service = RoomService(db=db)
    new_room = await room_service.create_room(data=room_data, owner=owner)
    return new_room

@router.post("/add_tenants")
async def add_tenants(room_id: str, tenant: RegisterRequest, db: AsyncSession = Depends(get_db), owner: User = Depends(require_owner)):
    room_service = RoomService(db=db)
    new_tenant = await room_service.link_room_to_user(room_id, tenant, owner)
    print(new_tenant)
    return new_tenant