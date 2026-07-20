from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationRepository:
    def create(self, db: Session, conversation: Conversation) -> Conversation:
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    def get_by_id(self, db: Session, conversation_id: int) -> Conversation | None:
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def list_for_user(self, db: Session, employee_id: int, user_id: int) -> list[Conversation]:
        return (
            db.query(Conversation)
            .filter(Conversation.employee_id == employee_id, Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .all()
        )


class MessageRepository:
    def create(self, db: Session, message: Message) -> Message:
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def list_for_conversation(self, db: Session, conversation_id: int) -> list[Message]:
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .all()
        )
