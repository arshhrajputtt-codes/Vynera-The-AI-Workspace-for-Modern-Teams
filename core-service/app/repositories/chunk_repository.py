from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.chunk import Chunk


class ChunkRepository:
    def bulk_create(self, db: Session, chunks: list[Chunk]) -> list[Chunk]:
        db.add_all(chunks)
        db.commit()
        for chunk in chunks:
            db.refresh(chunk)
        return chunks

    def delete_for_document(self, db: Session, document_id: int) -> None:
        db.execute(delete(Chunk).where(Chunk.document_id == document_id))
        db.commit()

    def search_similar(
        self,
        db: Session,
        employee_id: int,
        query_embedding: list[float],
        top_k: int,
    ) -> list[Chunk]:
        """
        Cosine-distance nearest-neighbor search, scoped to one employee's
        knowledge base. Requires the pgvector extension and an index such as:

            CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops);
        """
        return (
            db.query(Chunk)
            .filter(Chunk.employee_id == employee_id)
            .order_by(Chunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
            .all()
        )
