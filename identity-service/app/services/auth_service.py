from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.jwt import create_access_token
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin


class AuthService:
    def __init__(self, repository: UserRepository | None = None):
        # Accepting the repository as an optional constructor arg (rather
        # than hardcoding `UserRepository()`) is what makes this swappable
        # in unit tests — you can inject a fake repository without touching
        # the DB at all.
        self.repository = repository or UserRepository()

    def register_user(self, db: Session, data: UserCreate) -> User:
        if self.repository.get_by_email(db, data.email):
            raise UserAlreadyExistsError(data.email)

        user = User(
            email=data.email,
            password=hash_password(data.password),
        )
        return self.repository.create(db, user)

    def authenticate_user(self, db: Session, data: UserLogin) -> User:
        user = self.repository.get_by_email(db, data.email)

        if not user or not verify_password(data.password, user.password):
            # Deliberately the same error for "no such user" and "wrong
            # password" — distinguishing them lets an attacker enumerate
            # valid emails.
            raise InvalidCredentialsError()

        return user

    def create_token_for_user(self, user: User) -> str:
        return create_access_token({"user_id": user.id, "email": user.email})
