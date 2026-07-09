import uuid
from datetime import datetime
from sqlalchemy import (
    UUID,
    ForeignKey,
    String,
    DateTime,
    func
    )
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.db import Base
from auth.models import User
from rooms.models import Room

 
class Building(Base):
    __tablename__ = "buildings"
 
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="building", cascade="all, delete-orphan")
 
    def __repr__(self) -> str:
        return f"<Building id={self.id} name={self.name}>"
 