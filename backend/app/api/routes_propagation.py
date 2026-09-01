"""
JALNETRA API — Propagation Routes
"""

from fastapi import APIRouter
from datetime import datetime, timezone

from app.engines.propagation_engine import propagation_engine
from app.engines.risk_engine import risk_engine
from app.simulation.demo_controller import demo_controller
from app.schemas import PropagationResponse

router = APIRouter(prefix="/api", tags=["Propagation"])


@router.get("/propagation", response_model=PropagationResponse)
async def get_propagation():
    """
    Get current flood propagation prediction.

    Returns GeoJSON hazard geometry per timestep (T+0 through T+60).

    Note: PROTOTYPE SIMPLIFIED MODEL — not validated for operational use.
    """
    # Get current conditions
    sensor_data = demo_controller.get_sensor_overrides()

    # Get overall risk
    weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}
    risk_response = risk_engine.assess_all_zones(sensor_data, weather_data)

    # Find max risk probability
    max_risk = max(risk_response.zones, key=lambda z: z.risk_probability)

    # Run propagation
    return propagation_engine.propagate(
        risk_probability=max_risk.risk_probability,
        rainfall_mm=demo_controller.base_rainfall_mm * demo_controller.rainfall_multiplier,
        water_level_m=demo_controller.water_level_base,
        soil_moisture_percent=demo_controller.soil_moisture_base,
    )
