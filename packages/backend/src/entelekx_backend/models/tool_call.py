"""Tool call tracking model."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, DateTime, String, Text
from sqlmodel import Field, SQLModel


class ToolCall(SQLModel, table=True):
    """A single tool invocation tracked for approval, audit and result."""

    __tablename__ = "tool_calls"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message_id: UUID | None = Field(default=None, foreign_key="messages.id")
    session_id: UUID = Field(foreign_key="sessions.id")
    name: str = Field(sa_column=Column("name", String(255), nullable=False))
    arguments: dict = Field(default_factory=dict, sa_column=Column("arguments", JSON))
    result: dict = Field(default_factory=dict, sa_column=Column("result", JSON))
    status: str = Field(default="pending", sa_column=Column("status", String(50), nullable=False))
    approved_by: str | None = Field(default=None, sa_column=Column("approved_by", String(50)))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = Field(default=None, sa_column=Column("started_at", DateTime))
    completed_at: datetime | None = Field(default=None, sa_column=Column("completed_at", DateTime))
    rationale: str | None = Field(default=None, sa_column=Column("rationale", Text))
