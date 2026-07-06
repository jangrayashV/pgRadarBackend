class AppError(Exception):
    def __init__(self, message: str, code: str, status_code: int):
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class NotFoundError(AppError):
    def __init__(self, message: str):
        super().__init__(message, code="not_found", status_code=404)


class ConflictError(AppError):
    """Resource already exists or state conflict."""
    def __init__(self, message: str):
        super().__init__(message, code="conflict", status_code=409)


class ForbiddenError(AppError):
    """Authenticated but not authorized."""
    def __init__(self, message: str = "Access denied"):
        super().__init__(message, code="forbidden", status_code=403)


class AuthError(AppError):
    def __init__(self, message: str, code: str = "unauthorized"):
        super().__init__(message, code=code, status_code=401)


class ValidationError(AppError):
    """Business rule validation failure — different from Pydantic validation."""
    def __init__(self, message: str):
        super().__init__(message, code="validation_error", status_code=422)


class AccountLockedError(AuthError):
    def __init__(self, minutes_remaining: int):
        super().__init__(
            message=f"Account locked. Try again in {minutes_remaining} minutes.",
            code="account_locked",
        )