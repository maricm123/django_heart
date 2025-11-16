from typing import Any, Dict, Optional
from rest_framework import status


class DomainError(Exception):
    """
    Osnovna domain greška – nema pojma o HTTP-u kao protokolu,
    ali ipak držimo status_code jer nam odgovara u API sloju.
    """

    default_message = "Domain error."
    default_code = "domain_error"
    default_status_code = status.HTTP_400_BAD_REQUEST

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        *,
        field: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.field = field
        self.extra = extra or {}
        self.status_code = status_code or self.default_status_code
        super().__init__(self.message)


# Default errors
class DomainValidationError(DomainError):
    default_message = "Validation error."
    default_code = "validation_error"
    default_status_code = status.HTTP_400_BAD_REQUEST


class DomainPermissionError(DomainError):
    default_message = "You are not allowed to perform this action."
    default_code = "permission_denied"
    default_status_code = status.HTTP_403_FORBIDDEN


class DomainNotFoundError(DomainError):
    default_message = "Object not found."
    default_code = "not_found"
    default_status_code = status.HTTP_404_NOT_FOUND
