from sqlalchemy.orm import Session

from app.models.document import Document


class DocumentRepository:
    def create(self, db: Session, document: Document) -> Document:
        db.add(document)
        db.commit()
        db.refresh(document)
        return document

    def get_by_id(self, db: Session, document_id: int) -> Document | None:
        return db.query(Document).filter(Document.id == document_id).first()

    def list_for_employee(self, db: Session, employee_id: int) -> list[Document]:
        return db.query(Document).filter(Document.employee_id == employee_id).all()

    def update(self, db: Session, document: Document) -> Document:
        db.commit()
        db.refresh(document)
        return document

    def delete(self, db: Session, document: Document) -> None:
        db.delete(document)
        db.commit()
