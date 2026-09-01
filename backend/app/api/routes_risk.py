"""
JALNETRA API — Risk Routes
"""

from fastapi import APIRouter, Query
from datetime import datetime, timezone

from app.engines.risk_engine import risk_engine
from app.engines.propagation_engine import propagation_engine
from app.engines.impact_engine import impact_engine
from app.engines.safe_departure import safe_departure_engine
from app.simulation.demo_controller import demo_controller
from app.schemas import RiskResponse, DataFreshness

router = APIRouter(prefix="/api", tags=["Risk"])


@router.get("/risk", response_model=RiskResponse)
async def get_risk_assessment():
    """
    Get current risk assessment for all zones.

    Returns risk probability, level, confidence, trend, drivers,
    and model version for each zone.

    Note: Demo thresholds are NOT official disaster thresholds.
    """
    # Get current sensor data from demo controller
    sensor_data = demo_controller.get_sensor_overrides()

    # Get weather context
    weather_data = {
        "forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5,
    }

    return risk_engine.assess_all_zones(sensor_data, weather_data)


@router.get("/risk/{zone_id}")
async def get_zone_risk(zone_id: str):
    """Get risk assessment for a specific zone."""
    sensor_data = demo_controller.get_sensor_overrides()
    weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}

    response = risk_engine.assess_all_zones(sensor_data, weather_data)
    zone = next((z for z in response.zones if z.zone_id == zone_id), None)
    if not zone:
        from app.utils import JalnetraError, ErrorCode
        raise JalnetraError(404, ErrorCode.NOT_FOUND, f"Zone {zone_id} not found")
    return zone
