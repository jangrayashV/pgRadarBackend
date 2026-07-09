# @router.get("/my_dues")
# async def get_my_dues(tenant: User = Depends(get_tenant), db: AsyncSession = Depends(get_db)):
#     session = RentService(db)
#     return await session.get_my_dues(tenant)

# @router.get("/unpaid_dues/{tenant_id}")
# async def get_unpaid_dues(tenant_id, owner: User = Depends(get_owner), db: AsyncSession = Depends(get_db)):
#     session = RentService(db)
#     return await session.get_unpaid_dues(tenant_id)


import uuid as _uuid3
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
 
from rent.schemas import BuildingDuesResponse, RentEntryResponse, TenantDuesResponse
from rent.service import RentService
from core.db import get_db
from core.dependencies import require_owner, require_tenant
 
router = APIRouter(prefix="/rent", tags=["rent"])
 
 
@router.patch("/{entry_id}/mark-paid")
async def mark_paid(
    entry_id: _uuid3.UUID,
    owner: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
):
    service = RentService(db)
    await service.mark_paid(entry_id, _uuid3.UUID(owner["sub"]))
    return {"message": "Rent entry marked as paid."}
 
 
@router.get("/me/dues", response_model=TenantDuesResponse)
async def get_my_dues(
    tenant: dict = Depends(require_tenant),
    db: AsyncSession = Depends(get_db),
) -> TenantDuesResponse:
    service = RentService(db)
    result = await service.get_my_dues(_uuid3.UUID(tenant["sub"]))
    return TenantDuesResponse(
        entries=[RentEntryResponse.model_validate(e) for e in result["entries"]],
        total_outstanding=result["total_outstanding"],
    )
 
 
@router.get("/buildings/{building_id}/dues", response_model=BuildingDuesResponse)
async def get_building_dues(
    building_id: _uuid3.UUID,
    owner: dict = Depends(require_owner),
    db: AsyncSession = Depends(get_db),
) -> BuildingDuesResponse:
    service = RentService(db)
    result = await service.get_building_dues(building_id, _uuid3.UUID(owner["sub"]))
    return BuildingDuesResponse(
        building_id=result["building_id"],
        total_outstanding=result["total_outstanding"],
        entries=[RentEntryResponse.model_validate(e) for e in result["entries"]],
    )