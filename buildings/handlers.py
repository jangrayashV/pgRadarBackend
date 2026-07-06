from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from buildings.schemas import BuildingCreate, BuildingUpdate
from buildings.service import BuildingService
from core.db import get_db
from core.dependencies import get_owner


router = APIRouter()

@router.post("/buildings")
async def create_building(building_data: BuildingCreate, db: AsyncSession = Depends(get_db), owner=Depends(get_owner)):
    service = BuildingService(db)
    return await service.create_building(building_data, owner=owner)

@router.get("/{building_id}")
async def get_building(building_id: str, db: AsyncSession = Depends(get_db), owner=Depends(get_owner)):
    service = BuildingService(db)
    return await service.get_building(building_id)

@router.patch("/update_building/{building_id}")
async def update_building(building_id, updated_data: BuildingUpdate, db: AsyncSession = Depends(get_db), owner = Depends(get_owner)):
    service = BuildingService(db)
    return await service.update_building(building_id, updated_data)