from typing import Any, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Any] = None,
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class AccountNotFoundError(AppException):
    def __init__(self, account_id: str):
        super().__init__(
            code="ACCOUNT_NOT_FOUND",
            message=f"Account with ID '{account_id}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InsufficientBalanceError(AppException):
    def __init__(self, message: str = "The account does not have sufficient funds."):
        super().__init__(
            code="INSUFFICIENT_BALANCE",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class DuplicateTransactionReferenceError(AppException):
    def __init__(self, reference_id: str):
        super().__init__(
            code="DUPLICATE_TRANSACTION_REFERENCE",
            message=f"Transaction with reference '{reference_id}' already exists for this account.",
            status_code=status.HTTP_409_CONFLICT,
        )


class DuplicateTransferReferenceError(AppException):
    def __init__(self, reference_id: str):
        super().__init__(
            code="DUPLICATE_TRANSFER_REFERENCE",
            message=f"Transfer with reference '{reference_id}' already exists.",
            status_code=status.HTTP_409_CONFLICT,
        )


class SameAccountTransferError(AppException):
    def __init__(self):
        super().__init__(
            code="SAME_ACCOUNT_TRANSFER",
            message="Source and destination accounts must be different.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidTransactionTypeError(AppException):
    def __init__(self, type_val: str):
        super().__init__(
            code="INVALID_TRANSACTION_TYPE",
            message=f"Invalid transaction type '{type_val}'. Allowed values are 'credit' or 'debit'.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidAmountError(AppException):
    def __init__(self, message: str = "Amount must be a positive number with at most two decimal places."):
        super().__init__(
            code="INVALID_AMOUNT",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class InvalidPaginationError(AppException):
    def __init__(self, message: str = "Invalid pagination parameters."):
        super().__init__(
            code="INVALID_PAGINATION",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def format_error_response(code: str, message: str, details: Optional[Any] = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        ),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", []) if x != "body"])
        msg = err.get("msg", "Invalid value")
        details.append({"field": loc, "issue": msg})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_error_response(
            code="VALIDATION_ERROR",
            message="Request body or parameter validation failed.",
            details=details,
        ),
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code_map = {
        404: "NOT_FOUND",
        400: "BAD_REQUEST",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_SERVER_ERROR",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code=code,
            message=str(exc.detail),
            details=None,
        ),
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected server error occurred. Please try again later.",
            details=None,
        ),
    )
