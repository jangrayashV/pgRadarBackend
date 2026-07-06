from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from core.db import engine
from core.db import Base
from auth import models as auth_models
from buildings import models as building_models
from auth.handler import router as auth_router
from buildings.handlers import router as buildings_router
from rooms.handler import router as rooms_router
from rent.handlers import router as rent_router

from core.rate_limiter import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))

            # Create tables
            await conn.run_sync(Base.metadata.create_all)

        print("Database connected and tables created")

    except Exception as e:
        print("Database connection failed:", e)

    yield

    await engine.dispose()

app = FastAPI(lifespan=lifespan)



app.state.limiter = limiter

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(buildings_router, prefix="/buildings", tags=["buildings"])
app.include_router(rooms_router, prefix="/rooms", tags=["rooms"])
app.include_router(rent_router, prefix="/rent", tags=["rent_entries"])

@app.get("/")
async def root():
    return {"message": "Hello World"}


