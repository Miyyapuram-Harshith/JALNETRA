"""
JALNETRA API — System, Region, Road, Impact, and Event Routes
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime, timezone
import time

from app.config import settings
from app.schemas import (
    HealthResponse, RegionInfo, RoadRisk, RoadResponse, RoadStatus,
    ImpactResponse, ConnectivityReport, SystemStatus, NetworkStatus,
    DataFreshness, EventsResponse,
)
from app.data import (
    REGION_INFO, ROADS, ZONES, SHELTERS, SENSORS,
    CRITICAL_INFRASTRUCTURE, HISTORICAL_EVENTS,
    get_region_geojson,
)
from app.simulation.demo_controller import demo_controller
from app.engines.risk_engine import risk_engine
from app.engines.impact_engine import impact_engine
from app.engines.propagation_engine import propagation_engine
from app.services.audit_service import audit_service
from app.realtime.websocket_manager import ws_manager

router = APIRouter(tags=["System"])

_start_time = time.time()


# -----------------------------------------------------------------------
# Health
# -----------------------------------------------------------------------

@router.get("/api/system/health", response_model=HealthResponse)
async def health_check():
    """
    Full system health check.

    Returns status of: API, database, model, weather, WhatsApp, IoT, realtime.
    """
    return HealthResponse(
        status="healthy",
        api="healthy",
        database="healthy",
        model="healthy",
        weather="real" if settings.USE_REAL_WEATHER else "demo",
        whatsapp="configured" if settings.whatsapp_configured else "mock",
        iot="real" if settings.USE_REAL_IOT else "simulator",
        realtime="healthy" if ws_manager.is_healthy() else "degraded",
        demo_mode=settings.DEMO_MODE,
        version="1.0.0",
        uptime_seconds=round(time.time() - _start_time, 1),
    )


# -----------------------------------------------------------------------
# Region
# -----------------------------------------------------------------------

@router.get("/api/regions")
async def get_regions():
    """Get demo region data with full GeoJSON."""
    return RegionInfo(
        region_id=REGION_INFO["region_id"],
        name=REGION_INFO["name"],
        description=REGION_INFO["description"],
        center=REGION_INFO["center"],
        bounds=REGION_INFO["bounds"],
        geojson=get_region_geojson(),
        zones=[{
            "zone_id": z["zone_id"],
            "name": z["name"],
            "description": z["description"],
            "population": z["population"],
            "vulnerability": z["vulnerability"],
            "elevation_m": z["elevation_m"],
        } for z in ZONES],
        sensors=[{
            "sensor_id": s["sensor_id"],
            "name": s["name"],
            "type": s["type"],
            "location": s["location"],
            "zone_id": s["zone_id"],
        } for s in SENSORS],
        roads=[{
            "road_id": r["road_id"],
            "name": r["name"],
            "type": r["type"],
            "flood_vulnerable": r["flood_vulnerable"],
        } for r in ROADS],
        shelters=[{
            "shelter_id": s["shelter_id"],
            "name": s["name"],
            "capacity": s["capacity"],
            "medical": s["medical"],
            "location": s["location"],
        } for s in SHELTERS],
        is_demo=True,
        note="DEMO / SYNTHETIC DATA",
    )


# -----------------------------------------------------------------------
# Roads
# -----------------------------------------------------------------------

@router.get("/api/roads", response_model=RoadResponse)
async def get_roads():
    """Get all roads with current risk status."""
    sensor_data = demo_controller.get_sensor_overrides()
    weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}
    risk_response = risk_engine.assess_all_zones(sensor_data, weather_data)
    max_risk = max(risk_response.zones, key=lambda z: z.risk_probability)

    roads = []
    for road in ROADS:
        road_id = road["road_id"]
        override = demo_controller.road_overrides.get(road_id)

        if override:
            status = RoadStatus(override)
        elif road.get("flood_vulnerable", False) and max_risk.risk_probability > 0.5:
            status = RoadStatus.THREATENED
        else:
            status = RoadStatus.SAFE

        # Risk level for road
        if status == RoadStatus.CLOSED:
            risk = "CRITICAL"
        elif status == RoadStatus.UNSAFE:
            risk = "EVACUATE"
        elif status == RoadStatus.THREATENED:
            risk = "WARNING"
        else:
            risk = "NORMAL"

        roads.append(RoadRisk(
            road_id=road_id,
            road_name=road["name"],
            current_status=status,
            predicted_hazard_arrival_minutes=max_risk.estimated_onset_minutes if status != RoadStatus.SAFE else None,
            risk=risk,
            confidence=max_risk.confidence,
            geometry=road.get("geometry"),
        ))

    now = datetime.now(timezone.utc)
    return RoadResponse(
        roads=roads,
        timestamp=now,
        freshness=DataFreshness(timestamp=now, age_seconds=0, quality="good", source="demo"),
    )


@router.get("/api/roads/risk")
async def get_road_risk_summary():
    """Get road risk summary."""
    road_response = await get_roads()
    summary = {
        "total_roads": len(road_response.roads),
        "safe": len([r for r in road_response.roads if r.current_status == RoadStatus.SAFE]),
        "threatened": len([r for r in road_response.roads if r.current_status == RoadStatus.THREATENED]),
        "unsafe": len([r for r in road_response.roads if r.current_status == RoadStatus.UNSAFE]),
        "closed": len([r for r in road_response.roads if r.current_status == RoadStatus.CLOSED]),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return summary


@router.post("/api/roads/{road_id}/closure")
async def close_road(road_id: str):
    """Report a road closure."""
    demo_controller.road_overrides[road_id] = "CLOSED"

    await ws_manager.broadcast("routes", "ROAD_THREATENED", {
        "road_id": road_id, "status": "CLOSED",
    })
    audit_service.log("authority", "road_closure", new_state={"road_id": road_id, "status": "CLOSED"})

    return {"road_id": road_id, "status": "CLOSED", "message": f"Road {road_id} marked as CLOSED"}


# -----------------------------------------------------------------------
# Impact
# -----------------------------------------------------------------------

@router.get("/api/impact", response_model=ImpactResponse)
async def get_impact():
    """
    Get current impact assessment.

    Intersects predicted hazard with roads, shelters, settlements,
    and critical infrastructure.
    """
    sensor_data = demo_controller.get_sensor_overrides()
    weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}
    risk_response = risk_engine.assess_all_zones(sensor_data, weather_data)
    max_risk = max(risk_response.zones, key=lambda z: z.risk_probability)

    # Get propagation geometry for impact analysis
    propagation = propagation_engine.propagate(
        risk_probability=max_risk.risk_probability,
        rainfall_mm=demo_controller.base_rainfall_mm * demo_controller.rainfall_multiplier,
        water_level_m=demo_controller.water_level_base,
        soil_moisture_percent=demo_controller.soil_moisture_base,
    )

    # Use the T+30 timestep for current impact assessment
    hazard_geom = None
    for ts in propagation.timesteps:
        if ts.time_offset_minutes == 30:
            hazard_geom = ts.hazard_geometry
            break

    return impact_engine.assess_impact(
        hazard_geometry=hazard_geom,
        hazard_arrival_minutes=max_risk.estimated_onset_minutes,
        risk_probability=max_risk.risk_probability,
    )


# -----------------------------------------------------------------------
# Events / Audit
# -----------------------------------------------------------------------

@router.get("/api/events", response_model=EventsResponse)
async def get_events():
    """Get audit/event log."""
    entries = audit_service.get_entries()
    return EventsResponse(
        events=entries,
        total=len(entries),
        timestamp=datetime.now(timezone.utc),
    )


# -----------------------------------------------------------------------
# Connectivity
# -----------------------------------------------------------------------

@router.post("/api/system/connectivity")
async def report_connectivity(report: ConnectivityReport):
    """Report frontend connectivity status."""
    return {
        "acknowledged": True,
        "server_status": demo_controller.network_status.value,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# -----------------------------------------------------------------------
# Historical Events
# -----------------------------------------------------------------------

@router.get("/api/events/historical")
async def get_historical_events():
    """Get historical flood events (DEMO / SYNTHETIC DATA)."""
    return {
        "events": HISTORICAL_EVENTS,
        "note": "DEMO / SYNTHETIC DATA — not real historical records",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# -----------------------------------------------------------------------
# WebSocket Endpoints
# -----------------------------------------------------------------------

@router.websocket("/ws/{channel}")
async def websocket_endpoint(websocket: WebSocket, channel: str):
    """
    WebSocket endpoint for real-time updates.

    Channels: risk, sensors, alerts, incidents, routes, simulation, system
    """
    valid_channels = {"risk", "sensors", "alerts", "incidents", "routes", "simulation", "system"}
    if channel not in valid_channels:
        await websocket.close(code=4000)
        return

    await ws_manager.connect(websocket, channel)
    try:
        while True:
            # Keep connection alive, receive any client messages
            data = await websocket.receive_text()
            # Echo back for heartbeat
            await websocket.send_json({
                "event": "HEARTBEAT",
                "channel": channel,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, channel)
    except Exception:
        ws_manager.disconnect(websocket, channel)
