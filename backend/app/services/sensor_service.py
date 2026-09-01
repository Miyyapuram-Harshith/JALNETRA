"""
JALNETRA Sensor Service
=======================
Sensor trust engine: validates readings, computes health/quality/reliability
scores, detects anomalies. Does NOT silently delete anomalous data.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import logging

from app.data import SENSORS
from app.schemas import SensorHealth, SensorStatus, SensorResponse, DataFreshness

logger = logging.getLogger("jalnetra.sensor_service")


# Validation ranges per sensor type
VALID_RANGES = {
    "rainfall": {"rainfall_mm": (0, 500)},
    "water_level": {"water_level_m": (0, 20)},
    "soil_moisture": {"soil_moisture_percent": (0, 100)},
    "temperature": {"temperature_c": (-20, 60)},
    "humidity": {"humidity_percent": (0, 100)},
}

# Maximum rate of change per minute
MAX_RATE_OF_CHANGE = {
    "rainfall_mm": 50,
    "water_level_m": 2.0,
    "soil_moisture_percent": 10,
    "temperature_c": 5,
    "humidity_percent": 15,
}


class SensorService:
    """Sensor trust engine — validates, scores, and monitors sensor health."""

    def __init__(self):
        self._previous_readings: Dict[str, Dict] = {}
        self._anomaly_log: Dict[str, List[str]] = {}
        self._reading_counts: Dict[str, int] = {}

    def validate_reading(self, sensor_id: str, reading: Dict) -> Tuple[bool, List[str]]:
        """
        Validate a sensor reading.

        Returns:
            (is_valid, list_of_anomaly_descriptions)
        """
        anomalies = []
        sensor_meta = next((s for s in SENSORS if s["sensor_id"] == sensor_id), None)

        if not sensor_meta:
            return False, ["Unknown sensor ID"]

        sensor_type = sensor_meta.get("type", "unknown")
        valid_ranges = VALID_RANGES.get(sensor_type, {})

        # Check value ranges
        for field, (low, high) in valid_ranges.items():
            value = reading.get(field)
            if value is not None:
                if value < low or value > high:
                    anomalies.append(f"impossible_value: {field}={value} outside [{low},{high}]")

        # Check rate of change
        prev = self._previous_readings.get(sensor_id)
        if prev:
            for field, max_rate in MAX_RATE_OF_CHANGE.items():
                curr_val = reading.get(field)
                prev_val = prev.get(field)
                if curr_val is not None and prev_val is not None:
                    delta = abs(curr_val - prev_val)
                    if delta > max_rate:
                        anomalies.append(f"spike_detected: {field} changed by {delta:.1f} (max: {max_rate})")

        # Check for stuck values (duplicate)
        if prev:
            matching_fields = 0
            total_fields = 0
            for key in ["rainfall_mm", "water_level_m", "soil_moisture_percent", "temperature_c", "humidity_percent"]:
                if key in reading and key in prev:
                    total_fields += 1
                    if reading[key] == prev[key]:
                        matching_fields += 1
            if total_fields > 0 and matching_fields == total_fields:
                count = self._reading_counts.get(sensor_id, 0)
                if count > 5:
                    anomalies.append("stuck_value: readings unchanged for multiple cycles")

        # Battery check
        battery = reading.get("battery_percent")
        if battery is not None and battery < 15:
            anomalies.append(f"battery_low: {battery}%")

        # Signal check
        signal = reading.get("signal_strength")
        if signal is not None and signal < 20:
            anomalies.append(f"weak_signal: {signal}")

        # Store for next comparison
        self._previous_readings[sensor_id] = reading.copy()
        self._reading_counts[sensor_id] = self._reading_counts.get(sensor_id, 0) + 1

        # Log anomalies (do NOT discard data)
        if anomalies:
            self._anomaly_log.setdefault(sensor_id, []).extend(anomalies)
            logger.warning(f"Sensor {sensor_id} anomalies: {anomalies}")

        is_valid = len([a for a in anomalies if "impossible_value" in a]) == 0
        return is_valid, anomalies

    def compute_health(self, sensor_id: str, reading: Optional[Dict]) -> SensorHealth:
        """Compute health, quality, and reliability scores for a sensor."""
        sensor_meta = next((s for s in SENSORS if s["sensor_id"] == sensor_id), None)
        if not sensor_meta:
            return SensorHealth(
                sensor_id=sensor_id, name="Unknown", type="unknown",
                status=SensorStatus.OFFLINE, health_score=0, quality_score=0,
                reliability_score=0,
            )

        anomalies = []
        status = SensorStatus.ONLINE
        health_score = 100.0
        quality_score = 100.0
        reliability_score = 100.0

        if not reading or reading.get("status") == "OFFLINE":
            return SensorHealth(
                sensor_id=sensor_id,
                name=sensor_meta["name"],
                type=sensor_meta["type"],
                status=SensorStatus.OFFLINE,
                health_score=0,
                quality_score=0,
                reliability_score=0,
                last_seen=None,
                battery_percent=0,
                signal_strength=0,
                anomalies=["sensor_offline"],
                location=sensor_meta.get("location", {}),
                freshness=DataFreshness(
                    timestamp=datetime.now(timezone.utc),
                    age_seconds=9999,
                    quality="offline",
                    source="none",
                ),
            )

        # Battery impact
        battery = reading.get("battery_percent", 100)
        if battery < 15:
            health_score -= 30
            anomalies.append("battery_critical")
            status = SensorStatus.BATTERY_LOW
        elif battery < 30:
            health_score -= 15
            anomalies.append("battery_low")

        # Signal impact
        signal = reading.get("signal_strength", 100)
        if signal < 20:
            quality_score -= 30
            anomalies.append("weak_signal")
            status = SensorStatus.DEGRADED
        elif signal < 50:
            quality_score -= 15

        # Anomaly check
        _, reading_anomalies = self.validate_reading(sensor_id, reading)
        if reading_anomalies:
            anomalies.extend(reading_anomalies)
            quality_score -= len(reading_anomalies) * 10
            if any("impossible" in a or "spike" in a for a in reading_anomalies):
                status = SensorStatus.ANOMALY
                reliability_score -= 25

        # Data age impact
        timestamp = reading.get("timestamp", datetime.now(timezone.utc))
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except Exception:
                timestamp = datetime.now(timezone.utc)

        now = datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        age_seconds = (now - timestamp).total_seconds()

        if age_seconds > 300:
            quality_score -= 20
            anomalies.append("stale_data")
        elif age_seconds > 120:
            quality_score -= 10

        # Clamp scores
        health_score = max(0, min(100, health_score))
        quality_score = max(0, min(100, quality_score))
        reliability_score = max(0, min(100, reliability_score))

        if reading.get("status") == "ANOMALY":
            status = SensorStatus.ANOMALY

        return SensorHealth(
            sensor_id=sensor_id,
            name=sensor_meta["name"],
            type=sensor_meta["type"],
            status=status,
            health_score=round(health_score, 1),
            quality_score=round(quality_score, 1),
            reliability_score=round(reliability_score, 1),
            last_seen=timestamp,
            battery_percent=battery,
            signal_strength=signal,
            anomalies=anomalies,
            location=sensor_meta.get("location", {}),
            freshness=DataFreshness(
                timestamp=timestamp,
                age_seconds=round(age_seconds, 1),
                quality="good" if quality_score > 70 else "degraded" if quality_score > 40 else "poor",
                source="demo" if reading.get("status") != "ONLINE" else "sensor",
            ),
        )

    def get_all_health(self, readings: Dict[str, Dict]) -> SensorResponse:
        """Get health status for all sensors."""
        sensors = []
        for sensor in SENSORS:
            sid = sensor["sensor_id"]
            reading = readings.get(sid)
            health = self.compute_health(sid, reading)
            sensors.append(health)

        now = datetime.now(timezone.utc)
        return SensorResponse(
            sensors=sensors,
            total=len(sensors),
            demo_mode=True,
            freshness=DataFreshness(
                timestamp=now, age_seconds=0, quality="good", source="demo"
            ),
        )

    def reset(self):
        """Reset all tracking state."""
        self._previous_readings.clear()
        self._anomaly_log.clear()
        self._reading_counts.clear()


# Singleton
sensor_service = SensorService()
