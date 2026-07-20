from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.chunk import Chunk
from app.repositories.chunk_repository import ChunkRepository
from app.services.embedding_service import EmbeddingService


class VectorSearchService:
    def __init__(
        self,
        chunk_repository: ChunkRepository | None = None,
        embedding_service: EmbeddingService | None = None,
    ):
        self.chunk_repository = chunk_repository or ChunkRepository()
        self.embedding_service = embedding_service or EmbeddingService()

    def search(self, db: Session, employee_id: int, query: str, top_k: int | None = None) -> list[Chunk]:
        query_embedding = self.embedding_service.embed_query(query)
        return self.chunk_repository.search_similar(
            db, employee_id, query_embedding, top_k or settings.TOP_K_CHUNKS
        )
