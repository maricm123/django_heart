import logging
from typing import Any, Dict, List

from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import exception_handler as drf_exception_handler

from apis.exceptions import DomainError

logger = logging.getLogger(__name__)


def _format_errors(detail: Any, default_code: str = "error") -> List[Dict[str, Any]]:
    """
    Pretvori šta god DRF/django baci u listu:
    [
      { "message": "...", "code": "validation_error", "field": "email" | null }
    ]
    """

    # string
    if isinstance(detail, str):
        return [{"message": detail, "code": default_code, "field": None}]

    # lista poruka
    if isinstance(detail, (list, tuple)):
        return [
            {"message": str(msg), "code": default_code, "field": None}
            for msg in detail
        ]

    # dict field -> message(s)
    if isinstance(detail, dict):
        errors = []

        for field, messages in detail.items():
            if not isinstance(messages, (list, tuple)):
                messages = [messages]

            # non-field errors
            key_is_non_field = field in (
                api_settings.NON_FIELD_ERRORS_KEY,  # "non_field_errors"
                "__all__",  # Django default
            )
            field_name = None if key_is_non_field else field

            for msg in messages:
                errors.append(
                    {
                        "message": str(msg),
                        "code": default_code,
                        "field": field_name,
                    }
                )

        return errors

    # fallback
    return [{"message": "Unexpected error.", "code": default_code, "field": None}]


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    Globalni DRF handler.
    - standardizuje izlaz
    - hvata Django ValidationError
    - podržava naše DomainError klase
    """

    # 1) Domain error – naš tip (vidi klase ispod)
    if isinstance(exc, DomainError):
        payload = {
            "errors": [
                {
                    "message": exc.message,
                    "code": exc.code,
                    "field": exc.field,
                    "extra": exc.extra or {},
                }
            ]
        }
        return Response(payload, status=exc.status_code)

    # 2) Django ValidationError -> DRF ValidationError
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(detail=exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

    # 3) Pustimo DRF da odradi svoje
    response = drf_exception_handler(exc, context)

    if response is None:
        # Neočekivan exception -> log + generički 500
        logger.exception("Unhandled exception", exc_info=exc)
        return Response(
            {
                "errors": [
                    {
                        "message": "Internal server error.",
                        "code": "server_error",
                        "field": None,
                    }
                ]
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # 4) Standardizuj payload
    detail = response.data.get("detail", response.data)
    # Ako je `detail` već struktura, `_format_errors` će se snaći
    errors = _format_errors(detail)

    response.data = {"errors": errors}

    return response
