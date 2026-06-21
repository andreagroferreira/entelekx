"""Domain models for EntelekX."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column, String, Text
from sqlmodel import Field, SQLModel

from entelekx_backend.models.tool_call import ToolCall

def utc_now():
    return datetime.now(UTC)


class BaseModel(SQLModel):
    """Base model with UUID primary key and timestamps."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class User(BaseModel, table=True):
    """Single operator account (multi-user later)."""

    __tablename__ = "users"

    username: str = Field(sa_column=Column("username", String(255), unique=True, nullable=False))
    password_hash: str = Field(sa_column=Column("password_hash", String(255), nullable=False))


class Project(BaseModel, table=True):
    """A project scopes most data in EntelekX."""

    __tablename__ = "projects"

    user_id: UUID = Field(foreign_key="users.id")
    name: str = Field(sa_column=Column("name", String(255), nullable=False))
    slug: str = Field(sa_column=Column("slug", String(255), nullable=False))
    description: str | None = Field(default=None, sa_column=Column("description", Text))
    settings: dict = Field(default_factory=dict, sa_column=Column("settings", JSON))


class Session(BaseModel, table=True):
    """A chat thread."""

    __tablename__ = "sessions"

    project_id: UUID = Field(foreign_key="projects.id")
    title: str | None = Field(default=None, sa_column=Column("title", String(255)))
    model: str | None = Field(default=None, sa_column=Column("model", String(255)))


class Message(BaseModel, table=True):
    """A chat message."""

    __tablename__ = "messages"

    session_id: UUID = Field(foreign_key="sessions.id")
    role: str = Field(sa_column=Column("role", String(50), nullable=False))
    content: str = Field(sa_column=Column("content", Text, nullable=False))
    tool_calls: list[dict] = Field(default_factory=list, sa_column=Column("tool_calls", JSON))
    tool_call_id: str | None = Field(default=None, sa_column=Column("tool_call_id", String(255)))
    extra: dict = Field(default_factory=dict, sa_column=Column("metadata", JSON))


class Memory(BaseModel, table=True):
    """An extracted fact about a project or user."""

    __tablename__ = "memories"

    project_id: UUID = Field(foreign_key="projects.id")
    content: str = Field(sa_column=Column("content", Text, nullable=False))
    source: str | None = Field(default=None, sa_column=Column("source", String(255)))


class Document(BaseModel, table=True):
    """A note or spec."""

    __tablename__ = "documents"

    project_id: UUID = Field(foreign_key="projects.id")
    title: str = Field(sa_column=Column("title", String(255), nullable=False))
    body: str = Field(sa_column=Column("body", Text, nullable=False))
    tags: list[str] = Field(default_factory=list, sa_column=Column("tags", JSON))


class ProviderConfig(BaseModel, table=True):
    """Encrypted API keys per provider."""

    __tablename__ = "provider_configs"

    provider: str = Field(sa_column=Column("provider", String(100), unique=True, nullable=False))
    encrypted_key: str = Field(sa_column=Column("encrypted_key", Text, nullable=False))
    settings: dict = Field(default_factory=dict, sa_column=Column("settings", JSON))
