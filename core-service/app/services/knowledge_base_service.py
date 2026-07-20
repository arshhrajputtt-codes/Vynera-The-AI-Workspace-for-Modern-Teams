from sqlalchemy.orm import Session

from app.core.exceptions import DocumentProcessingError, NotFoundError, ProviderError
from app.models.chunk import Chunk
from app.models.document import Document, DocumentStatus
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.services import ingestion_service
from app.services.embedding_service import EmbeddingService


class KnowledgeBaseService:
    def __init__(
        self,
        document_repository: DocumentRepository | None = None,
        chunk_repository: ChunkRepository | None = None,
        embedding_service: EmbeddingService | None = None,
    ):
        self.document_repository = document_repository or DocumentRepository()
        self.chunk_repository = chunk_repository or ChunkRepository()
        self.embedding_service = embedding_service or EmbeddingService()

    def upload_document(
        self,
        db: Session,
        workspace_id: int,
        employee_id: int,
        uploaded_by: int,
        filename: str,
        file_bytes: bytes,
    ) -> Document:
        file_type = ingestion_service.detect_file_type(filename)

        document = Document(
            workspace_id=workspace_id,
            employee_id=employee_id,
            uploaded_by=uploaded_by,
            filename=filename,
            file_type=file_type,
            status=DocumentStatus.PENDING,
        )
        document = self.document_repository.create(db, document)

        # Processed synchronously for v1 simplicity. Worth moving to a
        # background worker (Celery/RQ) once uploads are large/frequent
        # enough that the request would otherwise time out.
        try:
            self._process_document(db, document, file_bytes, file_type)
        except Exception as exc:
            document.status = DocumentStatus.FAILED
            document.error_message = str(exc)[:500]
            self.document_repository.update(db, document)
            raise DocumentProcessingError(str(exc)) from exc

        return document

    def _process_document(self, db: Session, document: Document, file_bytes: bytes, file_type) -> None:
        document.status = DocumentStatus.PROCESSING
        self.document_repository.update(db, document)

        text = ingestion_service.extract_text(file_bytes, file_type)
        pieces = ingestion_service.chunk_text(text)

        if pieces:
            embeddings = self.embedding_service.embed_texts(pieces)
            chunks = [
                Chunk(
                    document_id=document.id,
                    employee_id=document.employee_id,
                    workspace_id=document.workspace_id,
                    chunk_index=i,
                    content=piece,
                    token_count=len(piece.split()),
                    embedding=embedding,
                )
                for i, (piece, embedding) in enumerate(zip(pieces, embeddings))
            ]
            self.chunk_repository.bulk_create(db, chunks)

        document.status = DocumentStatus.READY
        self.document_repository.update(db, document)

    def get_document(self, db: Session, employee_id: int, document_id: int) -> Document:
        document = self.document_repository.get_by_id(db, document_id)
        if not document or document.employee_id != employee_id:
            raise NotFoundError("Document", document_id)
        return document

    def list_documents(self, db: Session, employee_id: int) -> list[Document]:
        return self.document_repository.list_for_employee(db, employee_id)

    def delete_document(self, db: Session, document: Document) -> None:
        self.chunk_repository.delete_for_document(db, document.id)
        self.document_repository.delete(db, document)
