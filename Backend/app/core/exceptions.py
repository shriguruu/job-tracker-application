from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppException(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
            }
        },
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    # Map common status codes to error codes
    code_map = {
        status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
        status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
        status.HTTP_403_FORBIDDEN: "FORBIDDEN",
        status.HTTP_404_NOT_FOUND: "NOT_FOUND",
        status.HTTP_409_CONFLICT: "CONFLICT",
        status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
        status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
    }
    code = code_map.get(exc.status_code, "ERROR")
    return error_response(
        status_code=exc.status_code,
        code=code,
        message=str(exc.detail),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Extract readable validation error messages
    error_messages = []
    for err in exc.errors():
        loc = " -> ".join([str(p) for p in err.get("loc", []) if p != "body"])
        msg = err.get("msg", "Invalid value")
        if loc:
            error_messages.append(f"{loc}: {msg}")
        else:
            error_messages.append(msg)

    message = "; ".join(error_messages) if error_messages else "Request validation failed"
    return error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="VALIDATION_ERROR",
        message=message,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected internal server error occurred.",
    )
