import enum

from sqlalchemy import JSON, Column, DateTime, Enum, Integer, Text
from sqlalchemy.sql import func

from app.db.database import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(Integer, nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # List of {"document_id", "chunk_id", "filename", "snippet"} — populated
    # only on assistant messages that drew on retrieved knowledge-base chunks.
    citations = Column(JSON, nullable=True)

    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
