"""
JALNETRA API — Simulation & Demo Control Routes
"""

from fastapi import APIRouter
from datetime import datetime, timezone

from app.schemas import SimulationRequest, SimulationResponse
from app.simulation.demo_controller import demo_controller
from app.engines.risk_engine import risk_engine
from app.services.alert_service import alert_service
from app.services.incident_service import incident_service
from app.services.sensor_service import sensor_service
from app.services.audit_service import audit_service
from app.realtime.websocket_manager import ws_manager

router = APIRouter(tags=["Simulation & Demo"])


# -----------------------------------------------------------------------
# Simulation
# -----------------------------------------------------------------------

@router.post("/api/simulation/run", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest):
    """
    Run a scenario simulation.

    Returns a timeline showing how conditions evolve over time.
    Scenarios: NORMAL, WATCH, WARNING, FLASH_FLOOD, LANDSLIDE_CASCADE,
    SENSOR_FAILURE, NETWORK_FAILURE, NEAR_MISS
    """
    result = demo_controller.run_simulation(request)
    audit_service.log("system", "simulation_run", details={
        "scenario": request.scenario.value,
        "duration": request.duration_minutes,
    })
    return result


# -----------------------------------------------------------------------
# Demo Controls
# -----------------------------------------------------------------------

@router.post("/api/demo/start")
async def demo_start():
    """
    Start the scripted jury demo sequence.

    Initiates progression: NORMAL → RAIN → WATCH → WARNING → FLOOD →
    ROAD THREATENED → ROUTE CHANGES → ALERT → SOS → RESPONDER
    """
    result = demo_controller.start_demo()

    await ws_manager.broadcast_all("DEMO_STARTED", result)
    audit_service.log("authority", "demo_started")

    return result


@router.post("/api/demo/pause")
async def demo_pause():
    """Pause the demo sequence."""
    result = demo_controller.pause_demo()
    await ws_manager.broadcast_all("DEMO_PAUSED", result)
    return result


@router.post("/api/demo/reset")
async def demo_reset():
    """
    Reset all demo state instantly.

    Resets: sensors, risk, propagation, roads, shelters,
    incidents, alerts, simulation state.
    """
    demo_controller.reset()
    risk_engine.reset()
    alert_service.reset()
    incident_service.reset()
    sensor_service.reset()

    await ws_manager.broadcast_all("DEMO_RESET", {
        "message": "All systems reset to NORMAL",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    audit_service.log("system", "demo_reset")

    return {
        "status": "reset",
        "message": "All systems reset to NORMAL conditions",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/api/demo/rainfall/increase")
async def demo_rainfall_increase():
    """Increase rainfall intensity for demo."""
    result = demo_controller.increase_rainfall()

    await ws_manager.broadcast("sensors", "RAINFALL_INCREASED", result)
    await ws_manager.broadcast("risk", "RISK_UPDATED", {
        "trigger": "rainfall_increase",
        "rainfall_mm": result["base_rainfall_mm"],
    })

    audit_service.log("authority", "demo_rainfall_increase", new_state=result)

    return result


@router.post("/api/demo/sensor/fail")
async def demo_sensor_fail(sensor_id: str = "sensor-water-02"):
    """Inject sensor failure."""
    result = demo_controller.fail_sensor(sensor_id)

    await ws_manager.broadcast("sensors", "SENSOR_OFFLINE", {
        "sensor_id": sensor_id,
    })

    audit_service.log("system", "demo_sensor_failure", details=result)

    return result


@router.post("/api/demo/road/close")
async def demo_road_close(road_id: str = "road-bridge"):
    """Close a road for demo."""
    result = demo_controller.close_road(road_id)

    await ws_manager.broadcast("routes", "ROAD_THREATENED", {
        "road_id": road_id,
        "status": "CLOSED",
    })

    audit_service.log("authority", "road_closure", new_state=result)

    return result


@router.post("/api/demo/network/degrade")
async def demo_network_degrade():
    """Simulate network degradation."""
    result = demo_controller.degrade_network()

    await ws_manager.broadcast("system", "NETWORK_DEGRADED", result)
    audit_service.log("system", "network_degraded")

    return result


@router.post("/api/demo/network/restore")
async def demo_network_restore():
    """Restore network to ONLINE."""
    result = demo_controller.restore_network()

    await ws_manager.broadcast("system", "NETWORK_RESTORED", result)
    audit_service.log("system", "network_restored")

    return result


@router.post("/api/demo/sos")
async def demo_sos():
    """Trigger a demo SOS from citizen."""
    from app.schemas import SOSRequest
    sos = SOSRequest(
        latitude=30.4480,
        longitude=78.0780,
        message="Water rising rapidly, need immediate assistance",
        people_count=3,
        medical_needed=False,
    )

    incident = incident_service.create_from_sos(sos)

    await ws_manager.broadcast("incidents", "INCIDENT_CREATED", {
        "incident_id": incident.id,
        "source": "demo_sos",
        "priority": incident.priority.value,
    })

    audit_service.log("citizen", "demo_sos", new_state={
        "incident_id": incident.id,
    })

    return {
        "incident": incident,
        "message": "Demo SOS triggered — incident created",
    }


@router.post("/api/demo/whatsapp")
async def demo_whatsapp():
    """Trigger a demo WhatsApp alert send."""
    from app.api.routes_alerts import _whatsapp
    from app.schemas import AlertType, AlertChannel, WhatsAppAlertRequest

    # Create and send alert
    sensor_data = demo_controller.get_sensor_overrides()
    weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}
    risk_response = risk_engine.assess_all_zones(sensor_data, weather_data)
    max_risk = max(risk_response.zones, key=lambda z: z.risk_probability)

    from app.engines.safe_departure import safe_departure_engine
    departure = safe_departure_engine.calculate(
        hazard_arrival_minutes=max_risk.estimated_onset_minutes or 60.0,
        road_statuses=demo_controller.road_overrides,
        risk_probability=max_risk.risk_probability,
        confidence_score=max_risk.confidence_score,
    )

    alert = alert_service.create_alert(
        zone_id="zone-riverside",
        alert_type=AlertType.WARNING,
        risk_level=max_risk.risk_level,
        channel=AlertChannel.WHATSAPP,
        language="en",
        risk_data={
            "estimated_onset_minutes": max_risk.estimated_onset_minutes,
            "confidence": max_risk.confidence.value,
        },
        departure_data={
            "safe_departure_window_minutes": departure.safe_departure_window_minutes,
            "recommended_shelter_name": departure.recommended_shelter_name,
            "recommended_route_name": departure.recommended_route.route_name if departure.recommended_route else "N/A",
        },
    )

    result = await _whatsapp.send_message(
        recipient="demo",
        message=alert.message,
    )

    from app.schemas import WhatsAppStatus
    alert_service.update_alert_status(alert.alert_id, WhatsAppStatus(result["status"]), result)

    await ws_manager.broadcast("alerts", "WHATSAPP_SENT", {
        "alert_id": alert.alert_id,
        "status": result["status"],
    })

    return {
        "alert": alert,
        "whatsapp_result": result,
        "message": "Demo WhatsApp alert triggered",
    }


@router.get("/api/demo/state")
async def demo_state():
    """Get current demo state."""
    return demo_controller.get_state()
