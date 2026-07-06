from collections.abc import AsyncGenerator
from core.config import settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL: str = settings.get_database_url()

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def generate_monthly_rent():
    async with AsyncSessionLocal() as db:
        # fetch all active tenant-room associations
        result = await db.execute(
            select(RoomUserAssociation)
        )
        associations = result.scalars().all()

        # create one rent entry per tenant
        for assoc in associations:
            entry = RentEntries(
                tenant_id=assoc.user_id,
                room_id=assoc.room_id,
                owner_id=assoc.owner_id,
                rent=assoc.tenant_rent,
                due_date=datetime.now(timezone.utc).replace(day=1),
                paid_at=None,
            )
            db.add(entry)
        
        await db.commit()