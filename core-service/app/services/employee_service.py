from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class EmployeeService:
    def __init__(self, repository: EmployeeRepository | None = None):
        self.repository = repository or EmployeeRepository()

    def create_employee(
        self, db: Session, workspace_id: int, created_by: int, data: EmployeeCreate
    ) -> Employee:
        employee = Employee(
            workspace_id=workspace_id,
            created_by=created_by,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
            model=data.model,
            temperature=data.temperature,
        )
        return self.repository.create(db, employee)

    def get_employee(self, db: Session, workspace_id: int, employee_id: int) -> Employee:
        employee = self.repository.get_by_id(db, employee_id)
        if not employee or employee.workspace_id != workspace_id:
            raise NotFoundError("Employee", employee_id)
        return employee

    def list_employees(self, db: Session, workspace_id: int) -> list[Employee]:
        return self.repository.list_for_workspace(db, workspace_id)

    def update_employee(
        self, db: Session, employee: Employee, data: EmployeeUpdate
    ) -> Employee:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(employee, field, value)
        return self.repository.update(db, employee)

    def delete_employee(self, db: Session, employee: Employee) -> None:
        self.repository.delete(db, employee)
