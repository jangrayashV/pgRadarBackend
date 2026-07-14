from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from core.db import engine
from core.db import Base
from auth import models as auth_models
from buildings import models as building_models
from rooms import models as room_models          
from rent import models as rent_models  
from auth.handler import router as auth_router
from buildings.handlers import router as buildings_router
from rooms.handler import router as rooms_router
from rent.handlers import router as rent_router
import logging
from core.rate_limiter import limiter
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from fastapi.middleware.cors import CORSMiddleware

origins = [
    "https://pgradar.lovable.app",
    "https://id-preview--ea5877ab-014a-4693-b3eb-b192cad15399.lovable.app",
    "https://ea5877ab-014a-4693-b3eb-b192cad15399.lovableproject.com",
]


 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
 
 
scheduler = AsyncIOScheduler()
 
 
async def generate_monthly_rent():
    """
    Runs daily at midnight.
    For each active room_user_association, checks if today matches
    the day of their assigned_at. If yes and no entry exists for this month,
    creates a new rent entry.
    """
    from datetime import datetime, timezone
    from core.db import AsyncSessionLocal
    from rooms.models import RoomUserAssociation
    from rent.service import RentService
    from sqlalchemy import select
 
    logger.info("Running monthly rent generation job")
 
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(RoomUserAssociation).where(RoomUserAssociation.vacated_at.is_(None))
        )
        associations = result.scalars().all()
 
        today = datetime.now(timezone.utc)
        rent_service = RentService(db)
 
        for assoc in associations:
            if assoc.assigned_at.day == today.day:
                # check if entry already exists for this month
                from rent.models import RentEntry
                from sqlalchemy import extract
                existing = await db.execute(
                    select(RentEntry).where(
                        RentEntry.tenant_id == assoc.tenant_id,
                        RentEntry.room_id == assoc.room_id,
                        extract("month", RentEntry.due_date) == today.month,
                        extract("year", RentEntry.due_date) == today.year,
                    )
                )
                if existing.scalar_one_or_none():
                    continue  # already generated this month
 
                # need owner_id — fetch from building
                from rooms.models import Room
                from buildings.models import Building
                room = await db.get(Room, assoc.room_id)
                building = await db.get(Building, room.building_id)
 
                await rent_service.create_entry(
                    tenant_id=assoc.tenant_id,
                    room_id=assoc.room_id,
                    owner_id=building.owner_id,
                    amount=assoc.tenant_rent,
                )
 
        await db.commit()
        logger.info("Monthly rent generation complete")
 
 


@asynccontextmanager
async def lifespan(app: FastAPI):
    # create all tables on startup
    async with engine.begin() as conn:
        print("CREATING TABLES")
        await conn.run_sync(Base.metadata.create_all)
        print("TABLES CREATED")

    scheduler.add_job(
        generate_monthly_rent,
        CronTrigger(hour=0, minute=0),
    )
    scheduler.start()
    logger.info("Scheduler started")
    yield
    scheduler.shutdown()
    logger.info("Scheduler stopped")

app = FastAPI(
    title="pgRadar",
    description="Rent management system",
    version="1.0.0",
    lifespan=lifespan,
)
 
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,   # if using cookies
    allow_methods=["*"],
    allow_headers=["*"],
)


app.state.limiter = limiter

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(buildings_router, prefix="/buildings", tags=["buildings"])
app.include_router(rooms_router, prefix="/rooms", tags=["rooms"])
app.include_router(rent_router, prefix="/rent", tags=["rent_entries"])

 
@app.get("/")
async def health():
    return {"status": "ok"}
 