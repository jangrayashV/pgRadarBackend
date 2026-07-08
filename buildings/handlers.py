from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from buildings.schemas import BuildingCreateRequest, BuildingUpdateRequest, BuildingResponse
from buildings.service import BuildingService
from core.db import get_db
from core.dependencies import require_owner
import uuid as uuid_mod

router = APIRouter(prefix="/buildings", tags=["buildings"])
 
 
@router.post("", response_model=BuildingResponse)
async def create_building(
    body: BuildingCreateRequest,
    owner: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
) -> BuildingResponse:
    service = BuildingService(db)
    building = await service.create(
        owner_id=uuid_mod.UUID(owner["sub"]),
        name=body.name,
        address=body.address,
        city=body.city,
        state=body.state,
    )
    return BuildingResponse.model_validate(building)
 
 
@router.get("", response_model=list[BuildingResponse])
async def get_buildings(
    owner: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
) -> list[BuildingResponse]:
    service = BuildingService(db)
    buildings = await service.get_all(owner_id=uuid_mod.UUID(owner["sub"]))
    return [BuildingResponse.model_validate(b) for b in buildings]
 
 
@router.get("/{building_id}", response_model=BuildingResponse)
async def get_building(
    building_id: uuid_mod.UUID,
    owner: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
) -> BuildingResponse:
    service = BuildingService(db)
    building = await service.get_one(building_id, uuid_mod.UUID(owner["sub"]))
    return BuildingResponse.model_validate(building)
 
 
@router.patch("/{building_id}", response_model=BuildingResponse)
async def update_building(
    building_id: uuid_mod.UUID,
    body: BuildingUpdateRequest,
    owner: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
) -> BuildingResponse:
    service = BuildingService(db)
    building = await service.update(
        building_id=building_id,
        owner_id=uuid_mod.UUID(owner["sub"]),
        name=body.name,
        address=body.address,
        city=body.city,
        state=body.state,
    )
    return BuildingResponse.model_validate(building)
 
 
@router.delete("/{building_id}")
async def delete_building(
    building_id: uuid_mod.UUID,
    owner: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = BuildingService(db)
    await service.delete(building_id, uuid_mod.UUID(owner["sub"]))
    return {"message": "Building deleted."}
 