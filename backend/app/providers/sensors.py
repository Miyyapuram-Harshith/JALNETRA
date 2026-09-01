"""
JALNETRA Sensor Provider
========================
SensorProvider ABC with Simulated and Real implementations.
The rest of the application does not care which one is active.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional
import random
import math

from app.data import SENSORS, get_normal_readings


class SensorProvider(ABC):
    """Abstract base for sensor data providers."""

    @abstractmethod
    async def get_reading(self, sensor_id: str) -> Optional[Dict]:
        pass

    @abstractmethod
    async def get_all_readings(self) -> Dict[str, Dict]:
        pass

    @abstractmethod
    async def submit_reading(self, sensor_id: str, reading: Dict) -> bool:
        pass


class SimulatedSensorProvider(SensorProvider):
    """
    Generates simulated sensor readings for demo mode.
    Supports various scenarios: NORMAL, RISING, HIGH, ANOMALY, OFFLINE, BATTERY_LOW.
    """

    def __init__(self):
        self._readings: Dict[str, Dict] = {}
        self._scenarios: Dict[str, str] = {}  # sensor_id -> scenario
        self._base_readings = get_normal_readings()
        self._tick_count = 0  # For time-varying simulations
        self.reset()

    def reset(self):
        """Reset all sensors to normal baseline."""
        self._readings = {}
        self._scenarios = {}
        self._tick_count = 0
        for sensor in SENSORS:
            self._scenarios[sensor["sensor_id"]] = "NORMAL"
        self._update_readings()

    def set_scenario(self, sensor_id: str, scenario: str):
        """Set simulation scenario for a specific sensor."""
        if sensor_id in self._scenarios or sensor_id == "all":
            if sensor_id == "all":
                for sid in self._scenarios:
                    self._scenarios[sid] = scenario
            else:
                self._scenarios[sensor_id] = scenario
            self._update_readings()

    def tick(self):
        """Advance simulation by one step."""
        self._tick_count += 1
        self._update_readings()

    def _update_readings(self):
        """Regenerate readings based on current scenarios."""
        now = datetime.now(timezone.utc)

        for sensor in SENSORS:
            sid = sensor["sensor_id"]
            scenario = self._scenarios.get(sid, "NORMAL")
            base = self._base_readings.get(sid, {}).copy()

            if scenario == "OFFLINE":
                self._readings[sid] = {
                    "timestamp": now,
                    "status": "OFFLINE",
                    "battery_percent": 0,
                    "signal_strength": 0,
                }
                continue

            if scenario == "BATTERY_LOW":
                base["battery_percent"] = max(5, random.randint(3, 12))
                base["signal_strength"] = max(10, base.get("signal_strength", 50) - 30)

            # Apply scenario multipliers
            multiplier = self._get_multiplier(scenario)

            if "rainfall_mm" in base:
                base_rain = 2.5
                base["rainfall_mm"] = round(
                    base_rain * multiplier + random.gauss(0, 0.5 * multiplier), 1
                )
                base["rainfall_mm"] = max(0, base["rainfall_mm"])

            if "water_level_m" in base:
                base_level = 2.0
                base["water_level_m"] = round(
                    base_level + (multiplier - 1) * 1.5 + random.gauss(0, 0.1), 2
                )
                base["water_level_m"] = max(0.5, base["water_level_m"])

            if "soil_moisture_percent" in base:
                base_soil = 42.0
                base["soil_moisture_percent"] = round(
                    min(98, base_soil + (multiplier - 1) * 20 + random.gauss(0, 2)), 1
                )

            if scenario == "ANOMALY":
                # Inject anomalous spike
                if "rainfall_mm" in base:
                    base["rainfall_mm"] = round(random.uniform(200, 500), 1)
                if "water_level_m" in base:
                    base["water_level_m"] = round(random.uniform(8, 15), 2)

            base["timestamp"] = now
            base["status"] = "ANOMALY" if scenario == "ANOMALY" else "ONLINE"
            if scenario == "BATTERY_LOW":
                base["status"] = "BATTERY_LOW"

            self._readings[sid] = base

    def _get_multiplier(self, scenario: str) -> float:
        multipliers = {
            "NORMAL": 1.0,
            "RISING": 2.0 + self._tick_count * 0.3,
            "HIGH": 5.0 + self._tick_count * 0.2,
            "ANOMALY": 1.0,
            "OFFLINE": 0.0,
            "BATTERY_LOW": 1.0,
        }
        return min(multipliers.get(scenario, 1.0), 15.0)

    async def get_reading(self, sensor_id: str) -> Optional[Dict]:
        return self._readings.get(sensor_id)

    async def get_all_readings(self) -> Dict[str, Dict]:
        return dict(self._readings)

    async def submit_reading(self, sensor_id: str, reading: Dict) -> bool:
        """In simulation mode, accept external readings too."""
        reading["timestamp"] = datetime.now(timezone.utc)
        self._readings[sensor_id] = reading
        return True

    def get_sensor_status(self, sensor_id: str) -> str:
        reading = self._readings.get(sensor_id, {})
        return reading.get("status", "UNKNOWN")


class RealSensorProvider(SensorProvider):
    """
    Accepts real sensor readings via HTTP POST (e.g., from ESP32).
    Stores the latest reading per sensor.
    """

    def __init__(self):
        self._readings: Dict[str, Dict] = {}
        self._last_seen: Dict[str, datetime] = {}

    async def get_reading(self, sensor_id: str) -> Optional[Dict]:
        return self._readings.get(sensor_id)

    async def get_all_readings(self) -> Dict[str, Dict]:
        return dict(self._readings)

    async def submit_reading(self, sensor_id: str, reading: Dict) -> bool:
        """Store reading from real sensor."""
        reading["timestamp"] = datetime.now(timezone.utc)
        reading["status"] = "ONLINE"
        self._readings[sensor_id] = reading
        self._last_seen[sensor_id] = datetime.now(timezone.utc)
        return True

    def get_last_seen(self, sensor_id: str) -> Optional[datetime]:
        return self._last_seen.get(sensor_id)


def get_sensor_provider(use_real: bool = False) -> SensorProvider:
    """Factory: returns appropriate sensor provider based on config."""
    if use_real:
        return RealSensorProvider()
    return SimulatedSensorProvider()
