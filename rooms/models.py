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
from auth.models import User


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    number: Mapped[int] = mapped_column(Integer, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    building_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    vacancy: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    
class RoomUserAssociation(Base):
    __tablename__ = "room_user_association"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rooms.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    tenant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_email: Mapped[str] = mapped_column(String(255), nullable=False)
    tenant_rent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rent_paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    rent_due: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
