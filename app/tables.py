"""The database tables, described as Python classes (SQLAlchemy).

These describe storage only. The shapes the API sends and receives are the
Pydantic models in `schemas.py`.
"""

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RunStatus(StrEnum):
    queued = "queued"
    planning = "planning"
    running = "running"
    done = "done"
    failed = "failed"


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(Text)
    # Stored as text; a CHECK constraint makes the database reject any other value.
    status: Mapped[RunStatus] = mapped_column(
        Enum(RunStatus, name="run_status", native_enum=False, create_constraint=True)
    )
    # Empty (NULL) unless the Run failed.
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
