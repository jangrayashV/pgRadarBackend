from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from rent.schemas import RentEntryRequest
from auth.models import User
from core.dependencies import get_owner, get_tenant
from core.db import get_db
from rent.service import RentService

router = APIRouter()

@router.post("/add_entry")
async def add_entry(entry_data: RentEntryRequest, owner: User = Depends(get_owner), db: AsyncSession = Depends(get_db)):
    session = RentService(db)
    return await session.add_entry(entry_data=entry_data, owner=owner)

@router.get("/my_dues")
async def get_my_dues(tenant: User = Depends(get_tenant), db: AsyncSession = Depends(get_db)):
    session = RentService(db)
    return await session.get_my_dues(tenant)

@router.get("/unpaid_dues/{tenant_id}")
async def get_unpaid_dues(tenant_id, owner: User = Depends(get_owner), db: AsyncSession = Depends(get_db)):
    session = RentService(db)
    return await session.get_unpaid_dues(tenant_id)