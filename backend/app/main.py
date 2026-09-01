"""
JALNETRA — THE EYE BEFORE THE FLOOD
====================================
Hyperlocal Flash-Flood Intelligence, Evacuation & Last-Mile Alert Backend

FastAPI application entry point.
Run with: uvicorn app.main:app --reload
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import logging
import time

from app.config import settings
from app.utils import JalnetraError, jalnetra_error_handler, generic_error_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("jalnetra")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    logger.info("=" * 60)
    logger.info("  JALNETRA — THE EYE BEFORE THE FLOOD")
    logger.info("  Hyperlocal Flash-Flood Intelligence Backend")
    logger.info("=" * 60)
    logger.info(f"  Demo Mode: {settings.DEMO_MODE}")
    logger.info(f"  Database: {'SQLite (local)' if settings.is_sqlite else 'PostgreSQL'}")
    logger.info(f"  Weather: {'demo' if not settings.USE_REAL_WEATHER else 'real'}")
    logger.info(f"  IoT: {'simulator' if not settings.USE_REAL_IOT else 'real'}")
    logger.info(f"  WhatsApp: {settings.WHATSAPP_PROVIDER}")
    logger.info("=" * 60)

    # Initialize database
    try:
        from app.database import init_db
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"Database init skipped (using in-memory state): {e}")

    # Initialize demo data
    if settings.DEMO_MODE:
        logger.info("Loading demo data: Hilly Village Alpha")
        from app.simulation.demo_controller import demo_controller
        demo_controller.reset()
        logger.info("Demo data loaded — system ready")

    logger.info("")
    logger.info("  API docs: http://localhost:8000/docs")
    logger.info("  Health:   http://localhost:8000/api/system/health")
    logger.info("")

    yield

    # Shutdown
    try:
        from app.database import close_db
        await close_db()
    except Exception:
        pass
    logger.info("JALNETRA backend shutdown complete")


# ---------------------------------------------------------------------------
# App Factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="JALNETRA",
    description=(
        "THE EYE BEFORE THE FLOOD — "
        "Hyperlocal Flash-Flood Intelligence, Evacuation & Last-Mile Alert Backend. "
        "JALNETRA is a decision-support prototype. "
        "All predictions are modeled estimates, not guarantees."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_ORIGIN,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
        "*",  # Allow all for hackathon demo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------

app.add_exception_handler(JalnetraError, jalnetra_error_handler)


@app.exception_handler(Exception)
async def catch_all_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return await generic_error_handler(request, exc)


# ---------------------------------------------------------------------------
# Request Timing Middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def add_timing_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Process-Time"] = f"{duration:.4f}"
    response.headers["X-Jalnetra-Version"] = "1.0.0"
    return response


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.get("/", tags=["Root"])
async def root():
    """JALNETRA API root."""
    return {
        "name": "JALNETRA",
        "tagline": "THE EYE BEFORE THE FLOOD",
        "version": "1.0.0",
        "status": "operational",
        "demo_mode": settings.DEMO_MODE,
        "docs": "/docs",
        "health": "/api/system/health",
        "disclaimer": (
            "JALNETRA is a decision-support prototype. "
            "All predictions are modeled estimates, not guarantees of safety. "
            "This system is NOT an official government emergency service."
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Register Routers
# ---------------------------------------------------------------------------

from app.api.routes_risk import router as risk_router
from app.api.routes_sensors import router as sensor_router
from app.api.routes_forecast import router as forecast_router
from app.api.routes_propagation import router as propagation_router
from app.api.routes_routes import router as routes_router
from app.api.routes_shelters import router as shelters_router
from app.api.routes_incidents import router as incidents_router
from app.api.routes_alerts import router as alerts_router
from app.api.routes_simulation import router as simulation_router
from app.api.routes_system import router as system_router

app.include_router(risk_router)
app.include_router(sensor_router)
app.include_router(forecast_router)
app.include_router(propagation_router)
app.include_router(routes_router)
app.include_router(shelters_router)
app.include_router(incidents_router)
app.include_router(alerts_router)
app.include_router(simulation_router)
app.include_router(system_router)
