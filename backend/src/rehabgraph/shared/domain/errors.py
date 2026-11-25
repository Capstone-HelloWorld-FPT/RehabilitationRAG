"""Business errors. The HTTP layer maps DomainError → 422 (BACKEND-ARCHITECTURE section 8)."""


class DomainError(Exception):
    """A business rule was broken. `code` is UPPER_SNAKE_CASE, shared with the frontend vi.json."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
