from __future__ import annotations
from core.db import Base
from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    UUID
)
import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from buildings.models import Building  # only imported during type checking, not at runtime


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_number: Mapped[int] = mapped_column(Integer, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    rent_per_head: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    building: Mapped["Building"] = relationship("Building", back_populates="rooms")
    associations: Mapped[list["RoomUserAssociation"]] = relationship("RoomUserAssociation", back_populates="room", cascade="all, delete-orphan")
 
    def __repr__(self) -> str:
        return f"<Room id={self.id} building_id={self.building_id}>"
 

class RoomUserAssociation(Base):
    __tablename__ = "room_user_association"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rooms.id"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    tenant_rent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    vacated_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  
    assigned_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
    room: Mapped["Room"] = relationship("Room", back_populates="associations")  
    
    def __repr__(self) -> str:
        return f"<RoomUserAssociation room={self.room_id} tenant={self.tenant_id}>"
 