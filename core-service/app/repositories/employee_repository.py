from sqlalchemy.orm import Session

from app.models.employee import Employee


class EmployeeRepository:
    def create(self, db: Session, employee: Employee) -> Employee:
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee

    def get_by_id(self, db: Session, employee_id: int) -> Employee | None:
        return db.query(Employee).filter(Employee.id == employee_id).first()

    def list_for_workspace(self, db: Session, workspace_id: int) -> list[Employee]:
        return db.query(Employee).filter(Employee.workspace_id == workspace_id).all()

    def update(self, db: Session, employee: Employee) -> Employee:
        db.commit()
        db.refresh(employee)
        return employee

    def delete(self, db: Session, employee: Employee) -> None:
        db.delete(employee)
        db.commit()
