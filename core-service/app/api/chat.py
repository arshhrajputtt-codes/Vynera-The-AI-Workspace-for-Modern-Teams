import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.db.database import SessionLocal
from app.dependencies.auth import CurrentUser
from app.dependencies.workspace import require_workspace_role
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.chat import ChatRequest, ConversationResponse, MessageResponse
from app.services.chat_service import ChatService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/employees/{employee_id}",
    tags=["Chat"],
)

service = ChatService()
employee_repository = EmployeeRepository()


def _sse_encode(event: dict) -> str:
    return f"data: {json.dumps(event)}\n\n"


@router.post("/chat")
def chat(
    workspace_id: int,
    employee_id: int,
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("member")),
):
    employee = employee_repository.get_by_id(db, employee_id)
    if not employee or employee.workspace_id != workspace_id or not employee.is_active:
        raise HTTPException(status_code=404, detail="Employee not found")

    try:
        conversation = service.get_or_create_conversation(
            db, workspace_id, employee_id, current_user.id, data.conversation_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Detach the employee/conversation from `db` before the generator below
    # runs — FastAPI closes yield-dependencies like get_db() as soon as this
    # function returns, but StreamingResponse only starts iterating the
    # generator afterwards. Using `db` inside event_stream() would hit an
    # already-closed session. So the generator opens its own session instead.
    employee_id_value = employee.id
    conversation_id_value = conversation.id

    def event_stream():
        stream_db = SessionLocal()
        try:
            employee_local = employee_repository.get_by_id(stream_db, employee_id_value)
            conversation_local = service.conversation_repository.get_by_id(
                stream_db, conversation_id_value
            )
            yield _sse_encode({"type": "conversation_id", "conversation_id": conversation_id_value})
            for event in service.stream_reply(
                stream_db, conversation_local, employee_local, current_user.id, data.message
            ):
                yield _sse_encode(event)
        finally:
            stream_db.close()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    workspace_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("member")),
):
    return service.conversation_repository.list_for_user(db, employee_id, current_user.id)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def get_conversation_history(
    workspace_id: int,
    employee_id: int,
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("member")),
):
    try:
        conversation = service.get_or_create_conversation(
            db, workspace_id, employee_id, current_user.id, conversation_id
        )
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return service.list_history(db, conversation)
