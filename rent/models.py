from sqlalchemy import (
    UUID,
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    func,
    Float
)

from sqlalchemy.orm import mapped_column, Mapped
from core.db import Base
import uuid
from datetime import datetime


class RentEntries(Base):
    __tablename__="rent_entries"
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    room_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("rooms.id"), nullable=False)
    owner_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    rent: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default= func.now(), nullable=False)