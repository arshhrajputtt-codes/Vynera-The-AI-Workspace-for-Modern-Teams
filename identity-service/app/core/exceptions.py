class AppError(Exception):
    """Base class for domain/application errors (as opposed to bugs)."""


class UserAlreadyExistsError(AppError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"A user with email '{email}' already exists")


class InvalidCredentialsError(AppError):
    def __init__(self):
        super().__init__("Invalid email or password")


class InvalidTokenError(AppError):
    def __init__(self, reason: str = "Invalid or expired token"):
        super().__init__(reason)


class UserNotFoundError(AppError):
    def __init__(self, user_id: int | None = None):
        self.user_id = user_id
        super().__init__("User not found")


class NotWorkspaceMemberError(AppError):
    def __init__(self):
        super().__init__("You are not a member of this workspace")


class InsufficientRoleError(AppError):
    def __init__(self, required_role: str):
        self.required_role = required_role
        super().__init__(f"This action requires the '{required_role}' role or higher")


class AlreadyMemberError(AppError):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"'{email}' is already a member or has a pending invite")
