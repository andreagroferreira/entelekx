"""Base models and shared fields."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def utc_now():
    return datetime.now(timezone.utc)


class BaseModel(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
