from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import CurrentUser
from app.dependencies.workspace import require_workspace_role
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import EmployeeService

router = APIRouter(prefix="/workspaces/{workspace_id}/employees", tags=["AI Employees"])

service = EmployeeService()


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    workspace_id: int,
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    # Creating an employee is an admin-level action — members can chat with
    # employees, but shouldn't be able to reconfigure their prompts.
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    return service.create_employee(db, workspace_id, current_user.id, data)


@router.get("", response_model=list[EmployeeResponse])
def list_employees(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("member")),
):
    return service.list_employees(db, workspace_id)


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    workspace_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("member")),
):
    return service.get_employee(db, workspace_id, employee_id)


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    workspace_id: int,
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    employee = service.get_employee(db, workspace_id, employee_id)
    return service.update_employee(db, employee, data)


@router.delete("/{employee_id}")
def delete_employee(
    workspace_id: int,
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_workspace_role("admin")),
):
    employee = service.get_employee(db, workspace_id, employee_id)
    service.delete_employee(db, employee)
    return {"message": "Employee deleted successfully"}
