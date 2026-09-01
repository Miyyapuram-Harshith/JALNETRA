"""
JALNETRA Structured Error Handling
Consistent error codes and response format across the API.
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from typing import Any, Optional
import uuid


# ---------------------------------------------------------------------------
# Error Codes
# ---------------------------------------------------------------------------

class ErrorCode:
    # Sensor errors
    SENSOR_NOT_FOUND = "SENSOR_NOT_FOUND"
    INVALID_SENSOR_DATA = "INVALID_SENSOR_DATA"
    DUPLICATE_READING = "DUPLICATE_READING"
    SENSOR_OFFLINE = "SENSOR_OFFLINE"

    # Data errors
    STALE_DATA = "STALE_DATA"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"

    # Model errors
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    PREDICTION_FAILED = "PREDICTION_FAILED"

    # Route errors
    ROUTE_UNAVAILABLE = "ROUTE_UNAVAILABLE"
    NO_SAFE_ROUTE = "NO_SAFE_ROUTE"

    # Shelter errors
    SHELTER_FULL = "SHELTER_FULL"
    SHELTER_INACCESSIBLE = "SHELTER_INACCESSIBLE"

    # WhatsApp errors
    WHATSAPP_NOT_CONFIGURED = "WHATSAPP_NOT_CONFIGURED"
    WHATSAPP_PROVIDER_ERROR = "WHATSAPP_PROVIDER_ERROR"
    WHATSAPP_SEND_FAILED = "WHATSAPP_SEND_FAILED"

    # Simulation errors
    SIMULATION_FAILED = "SIMULATION_FAILED"
    INVALID_SCENARIO = "INVALID_SCENARIO"

    # Incident errors
    INCIDENT_NOT_FOUND = "INCIDENT_NOT_FOUND"

    # Auth errors
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # General
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NOT_FOUND = "NOT_FOUND"


# ---------------------------------------------------------------------------
# Error Response
# ---------------------------------------------------------------------------

class JalnetraError(HTTPException):
    """Custom exception with structured error response."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[dict] = None,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.request_id = str(uuid.uuid4())[:8]
        super().__init__(status_code=status_code, detail=message)


async def jalnetra_error_handler(request: Request, exc: JalnetraError) -> JSONResponse:
    """Global handler for JalnetraError exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": exc.timestamp,
            "request_id": exc.request_id,
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "code": ErrorCode.INTERNAL_ERROR,
            "message": "An internal error occurred. The system continues to operate.",
            "details": {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": str(uuid.uuid4())[:8],
        },
    )
