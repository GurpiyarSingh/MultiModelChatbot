from datetime import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(pattern="^(system|user|assistant)$")
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, description="The user's next message.")
    model: str | None = Field(default=None, description="Model name; defaults to DEFAULT_MODEL.")
    session_id: str | None = Field(default=None, description="Existing session to continue.")


class ChatResponse(BaseModel):
    session_id: str
    model: str
    message: Message


class SessionSummary(BaseModel):
    id: str
    model: str
    message_count: int
    updated_at: datetime


class SessionDetail(SessionSummary):
    messages: list[Message]


class ModelInfo(BaseModel):
    id: str
    provider: str
    available: bool
