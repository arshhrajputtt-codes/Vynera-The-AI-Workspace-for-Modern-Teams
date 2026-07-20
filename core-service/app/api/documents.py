from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.exceptions import DocumentProcessingError, NotFoundError, ProviderError, UnsupportedFileTypeError
from app.db.session import get_db
from app.dependencies.auth import CurrentUser
from app.dependencies.workspace import require_workspace_role
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.document import DocumentResponse
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(
    prefix="/workspaces/{workspace_id}/employees/{employee_id}/documents",
    tags=["Knowledge Base"],
)

service = KnowledgeBaseService()
employee_repository = EmployeeRepository()

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    workspace_id: int,
    employee_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    employee = employee_repository.get_by_id(db, employee_id)
    if not employee or employee.workspace_id != workspace_id:
        raise HTTPException(status_code=404, detail="Employee not found")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 20MB limit")

    try:
        return service.upload_document(
            db, workspace_id, employee_id, current_user.id, file.filename, file_bytes
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    except DocumentProcessingError as exc:
        # Document row is already saved with status=FAILED and an
        # error_message at this point; this just tells the caller why.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("", response_model=list[DocumentResponse])
def list_documents(
    workspace_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("member")),
):
    return service.list_documents(db, employee_id)


@router.delete("/{document_id}")
def delete_document(
    workspace_id: int,
    employee_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    try:
        document = service.get_document(db, employee_id, document_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    service.delete_document(db, document)
    return {"message": "Document deleted successfully"}
