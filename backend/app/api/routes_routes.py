"""
JALNETRA API — Route & Safe Departure Routes
"""

from fastapi import APIRouter
from datetime import datetime, timezone

from app.engines.route_engine import route_engine
from app.engines.safe_departure import safe_departure_engine
from app.engines.risk_engine import risk_engine
from app.simulation.demo_controller import demo_controller
from app.schemas import RouteResponse, SafeDepartureWindow, DataFreshness

router = APIRouter(prefix="/api", tags=["Routes"])


@router.get("/routes", response_model=RouteResponse)
async def get_routes():
    """
    Get available routes with risk assessment and safe departure window.

    Returns ranked candidate routes (safest first) with travel time,
    hazard arrival, safety margin, and the central Safe Departure Window.
    """
    # Get current risk for context
    sensor_data = demo_controller.get_sensor_overrides()
    weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}
    risk_response = risk_engine.assess_all_zones(sensor_data, weather_data)

    max_risk = max(risk_response.zones, key=lambda z: z.risk_probability)
    risk_prob = max_risk.risk_probability

    # Build hazard arrival estimates per road
    hazard_arrivals = {}
    if max_risk.estimated_onset_minutes:
        from app.data import ROADS
        for road in ROADS:
            if road.get("flood_vulnerable", False):
                hazard_arrivals[road["road_id"]] = max_risk.estimated_onset_minutes

    # Calculate routes
    routes = route_engine.calculate_routes(
        road_statuses=demo_controller.road_overrides,
        hazard_arrivals=hazard_arrivals,
        risk_probability=risk_prob,
    )

    # Calculate safe departure window
    hazard_arrival = max_risk.estimated_onset_minutes or 60.0
    safe_departure = safe_departure_engine.calculate(
        hazard_arrival_minutes=hazard_arrival,
        road_statuses=demo_controller.road_overrides,
        hazard_arrivals=hazard_arrivals,
        risk_probability=risk_prob,
        confidence_score=max_risk.confidence_score,
    )

    now = datetime.now(timezone.utc)
    return RouteResponse(
        routes=routes,
        safe_departure=safe_departure,
        timestamp=now,
        freshness=DataFreshness(
            timestamp=now, age_seconds=0, quality="modeled", source="demo"
        ),
    )


@router.get("/departure-window", response_model=SafeDepartureWindow)
async def get_departure_window():
    """
    Get the Safe Departure Window — central JALNETRA intelligence feature.

    Calculates: hazard_arrival - travel_time - safety_buffer

    Always labeled: MODELED ESTIMATE
    """
    sensor_data = demo_controller.get_sensor_overrides()
    weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}
    risk_response = risk_engine.assess_all_zones(sensor_data, weather_data)

    max_risk = max(risk_response.zones, key=lambda z: z.risk_probability)

    hazard_arrivals = {}
    if max_risk.estimated_onset_minutes:
        from app.data import ROADS
        for road in ROADS:
            if road.get("flood_vulnerable", False):
                hazard_arrivals[road["road_id"]] = max_risk.estimated_onset_minutes

    return safe_departure_engine.calculate(
        hazard_arrival_minutes=max_risk.estimated_onset_minutes or 60.0,
        road_statuses=demo_controller.road_overrides,
        hazard_arrivals=hazard_arrivals,
        risk_probability=max_risk.risk_probability,
        confidence_score=max_risk.confidence_score,
    )
