"""
JALNETRA API — Shelter Routes
"""

from fastapi import APIRouter
from datetime import datetime, timezone

from app.data import SHELTERS, ROADS
from app.schemas import ShelterInfo, ShelterResponse, RoadStatus, DataFreshness
from app.simulation.demo_controller import demo_controller
from app.engines.risk_engine import risk_engine

router = APIRouter(prefix="/api", tags=["Shelters"])


@router.get("/shelters", response_model=ShelterResponse)
async def get_shelters():
    """
    Get all shelters with capacity, accessibility, and ranking.

    Shelters are ranked based on predicted safety, route viability,
    travel time, and capacity. If a shelter becomes inaccessible,
    alternatives are recommended.
    """
    sensor_data = demo_controller.get_sensor_overrides()
    weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}
    risk_response = risk_engine.assess_all_zones(sensor_data, weather_data)
    max_risk = max(risk_response.zones, key=lambda z: z.risk_probability)
    risk_prob = max_risk.risk_probability

    shelters = []
    shelter_elevations = {}  # Track elevation for sorting

    for i, shelter_data in enumerate(SHELTERS):
        # Determine access status
        current_access = RoadStatus.SAFE
        predicted_access = RoadStatus.SAFE

        # Check if access roads are overridden
        access_roads = shelter_data.get("access_roads", [])
        for road_id in access_roads:
            override = demo_controller.road_overrides.get(road_id)
            if override == "CLOSED":
                current_access = RoadStatus.CLOSED
                predicted_access = RoadStatus.CLOSED
                break
            elif override == "UNSAFE":
                current_access = RoadStatus.UNSAFE

        # If high risk and low elevation, predict access degradation
        if risk_prob > 0.5 and shelter_data.get("elevation_m", 1000) < 900:
            predicted_access = RoadStatus.THREATENED

        # Calculate travel time based on road data
        travel_time = None
        for road_id in access_roads:
            road = next((r for r in ROADS if r["road_id"] == road_id), None)
            if road:
                if travel_time is None:
                    travel_time = road["travel_time_minutes"]
                else:
                    travel_time = min(travel_time, road["travel_time_minutes"])

        sid = shelter_data["shelter_id"]
        shelter_elevations[sid] = shelter_data.get("elevation_m", 0)

        shelters.append(ShelterInfo(
            shelter_id=sid,
            name=shelter_data["name"],
            capacity=shelter_data["capacity"],
            occupancy=shelter_data.get("occupancy", 0),
            available_capacity=shelter_data["capacity"] - shelter_data.get("occupancy", 0),
            medical=shelter_data.get("medical", False),
            water=shelter_data.get("water", True),
            power=shelter_data.get("power", True),
            accessibility=shelter_data.get("accessibility", "accessible"),
            current_access=current_access,
            predicted_access=predicted_access,
            travel_time_minutes=travel_time,
            location=shelter_data["location"],
            rank=i + 1,
        ))

    # Re-rank: accessible shelters first, then by elevation (higher = safer)
    shelters.sort(
        key=lambda s: (
            0 if s.current_access == RoadStatus.SAFE else 1,
            0 if s.predicted_access == RoadStatus.SAFE else 1,
            -shelter_elevations.get(s.shelter_id, 0),
        )
    )
    for i, s in enumerate(shelters):
        s.rank = i + 1

    now = datetime.now(timezone.utc)
    return ShelterResponse(
        shelters=shelters,
        timestamp=now,
        freshness=DataFreshness(
            timestamp=now, age_seconds=0, quality="good", source="demo"
        ),
    )
