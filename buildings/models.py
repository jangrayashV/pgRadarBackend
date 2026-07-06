import uuid
from datetime import datetime
from sqlalchemy import (
    UUID,
    Select,
    ForeignKey,
    String,
    DateTime,
    Integer,
    Boolean
    )
from sqlalchemy.orm import Mapped, mapped_column
from core.db import Base
from auth.models import User

class Building(Base):
    __tablename__ = "buildings"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    