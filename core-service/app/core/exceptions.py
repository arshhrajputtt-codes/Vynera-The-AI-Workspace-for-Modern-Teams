class AppError(Exception):
    """Base class for domain/application errors."""


class NotFoundError(AppError):
    def __init__(self, entity: str, entity_id: int | str):
        self.entity = entity
        self.entity_id = entity_id
        super().__init__(f"{entity} {entity_id} not found")


class ForbiddenError(AppError):
    def __init__(self, reason: str = "You don't have access to this resource"):
        super().__init__(reason)


class InvalidTokenError(AppError):
    def __init__(self, reason: str = "Invalid or expired token"):
        super().__init__(reason)


class UnsupportedFileTypeError(AppError):
    def __init__(self, filename: str):
        self.filename = filename
        super().__init__(f"Unsupported file type: {filename}")


class ProviderError(AppError):
    """Raised when an upstream LLM/embedding provider call fails."""

    def __init__(self, provider: str, detail: str):
        self.provider = provider
        super().__init__(f"{provider} error: {detail}")


class DocumentProcessingError(AppError):
    """Raised when text extraction/chunking/embedding fails for an uploaded file."""

    def __init__(self, detail: str):
        super().__init__(f"Failed to process document: {detail}")
