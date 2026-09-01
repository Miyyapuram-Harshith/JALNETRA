"""
JALNETRA API — Sensor Routes
"""

from fastapi import APIRouter, Path
from datetime import datetime, timezone

from app.schemas import (
    SensorReading, SensorSimulateRequest, SensorResponse,
    SensorHealth, SimulationScenario, DataFreshness,
)
from app.services.sensor_service import sensor_service
from app.simulation.demo_controller import demo_controller
from app.realtime.websocket_manager import ws_manager
from app.services.audit_service import audit_service
from app.data import SENSORS
from app.utils import JalnetraError, ErrorCode

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])


@router.get("", response_model=SensorResponse)
async def get_all_sensors():
    """
    Get all sensors with health status.

    Returns health_score, quality_score, reliability_score,
    battery, signal, anomalies, and freshness per sensor.
    """
    readings = demo_controller.get_sensor_overrides()
    return sensor_service.get_all_health(readings)


@router.get("/{sensor_id}", response_model=SensorHealth)
async def get_sensor(sensor_id: str = Path(..., description="Sensor ID")):
    """Get detailed status for a specific sensor."""
    sensor_meta = next((s for s in SENSORS if s["sensor_id"] == sensor_id), None)
    if not sensor_meta:
        raise JalnetraError(404, ErrorCode.SENSOR_NOT_FOUND, f"Sensor {sensor_id} not found")

    readings = demo_controller.get_sensor_overrides()
    reading = readings.get(sensor_id)
    return sensor_service.compute_health(sensor_id, reading)


@router.post("/{sensor_id}/reading")
async def submit_reading(
    sensor_id: str = Path(..., description="Sensor ID"),
    reading: SensorReading = ...,
):
    """
    Submit a sensor reading (ESP32 compatible).

    Validates units, timestamp, range, device ID, duplicate readings,
    and abnormal rate of change.
    """
    sensor_meta = next((s for s in SENSORS if s["sensor_id"] == sensor_id), None)
    if not sensor_meta:
        raise JalnetraError(404, ErrorCode.SENSOR_NOT_FOUND, f"Sensor {sensor_id} not found")

    # Convert to dict for validation
    reading_dict = reading.model_dump(exclude_none=True)
    is_valid, anomalies = sensor_service.validate_reading(sensor_id, reading_dict)

    if not is_valid:
        raise JalnetraError(
            422, ErrorCode.INVALID_SENSOR_DATA,
            f"Invalid sensor data: {', '.join(anomalies)}",
            details={"anomalies": anomalies},
        )

    # Broadcast sensor update
    await ws_manager.broadcast("sensors", "SENSOR_UPDATED", {
        "sensor_id": sensor_id,
        "reading": reading_dict,
        "anomalies": anomalies,
    })

    audit_service.log("sensor", "sensor_reading_received", details={
        "sensor_id": sensor_id, "anomalies": anomalies
    })

    return {
        "status": "accepted",
        "sensor_id": sensor_id,
        "anomalies": anomalies,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/{sensor_id}/simulate")
async def simulate_sensor(
    sensor_id: str = Path(..., description="Sensor ID"),
    request: SensorSimulateRequest = ...,
):
    """
    Trigger a simulation scenario on a sensor.

    Scenarios: NORMAL, RISING, HIGH, ANOMALY, OFFLINE, BATTERY_LOW
    """
    sensor_meta = next((s for s in SENSORS if s["sensor_id"] == sensor_id), None)
    if not sensor_meta:
        raise JalnetraError(404, ErrorCode.SENSOR_NOT_FOUND, f"Sensor {sensor_id} not found")

    scenario_name = request.scenario.value

    # Broadcast scenario change
    await ws_manager.broadcast("sensors", "SENSOR_SCENARIO_CHANGED", {
        "sensor_id": sensor_id,
        "scenario": scenario_name,
    })

    if scenario_name == "OFFLINE":
        await ws_manager.broadcast("sensors", "SENSOR_OFFLINE", {"sensor_id": sensor_id})
    elif scenario_name == "ANOMALY":
        await ws_manager.broadcast("sensors", "SENSOR_ANOMALY", {"sensor_id": sensor_id})

    audit_service.log("system", "sensor_simulation", details={
        "sensor_id": sensor_id, "scenario": scenario_name
    })

    return {
        "status": "scenario_applied",
        "sensor_id": sensor_id,
        "scenario": scenario_name,
        "message": f"Sensor {sensor_id} set to {scenario_name}",
    }
