"""
JALNETRA Demo Controller
=========================
Manages the scripted jury demo: step-by-step progression through
NORMAL → CRISIS → RESPONSE → RECOVERY with controllable timing.

Also handles simulation scenarios and demo state management.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import asyncio
import uuid
import logging

from app.schemas import (
    RiskLevel, RiskTrend, DemoScenario, SimulationRequest,
    SimulationResponse, SimulationTimelinePoint, NetworkStatus,
)

logger = logging.getLogger("jalnetra.demo")


class DemoController:
    """
    Controls the demo state machine.

    Manages:
    - Sensor readings (via sensor provider)
    - Weather conditions (via weather provider)
    - Road statuses
    - Network status
    - Demo scenario progression
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all demo state to NORMAL."""
        self.current_scenario = DemoScenario.NORMAL
        self.rainfall_multiplier = 1.0
        self.base_rainfall_mm = 5.0
        self.water_level_base = 2.0
        self.soil_moisture_base = 42.0
        self.road_overrides: Dict[str, str] = {}
        self.network_status = NetworkStatus.ONLINE
        self.is_running = False
        self.is_paused = False
        self.demo_step = 0
        self.demo_events: List[Dict] = []
        self._tick_count = 0

        logger.info("Demo state reset to NORMAL")

    def get_state(self) -> Dict:
        """Get current demo state."""
        return {
            "scenario": self.current_scenario.value,
            "rainfall_multiplier": self.rainfall_multiplier,
            "base_rainfall_mm": self.base_rainfall_mm,
            "water_level_base": self.water_level_base,
            "soil_moisture_base": self.soil_moisture_base,
            "road_overrides": self.road_overrides,
            "network_status": self.network_status.value,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "demo_step": self.demo_step,
            "tick_count": self._tick_count,
        }

    def tick(self):
        """Advance demo by one step."""
        self._tick_count += 1

    # -----------------------------------------------------------------------
    # Demo Controls
    # -----------------------------------------------------------------------

    def start_demo(self) -> Dict:
        """Start the scripted jury demo sequence."""
        self.reset()
        self.is_running = True
        self.demo_step = 1
        self._log_event("demo_started", "Jury demo sequence initiated")
        return {"status": "started", "step": 1, "message": "Demo started — NORMAL conditions"}

    def pause_demo(self) -> Dict:
        self.is_paused = True
        self._log_event("demo_paused", f"Paused at step {self.demo_step}")
        return {"status": "paused", "step": self.demo_step}

    def resume_demo(self) -> Dict:
        self.is_paused = False
        self._log_event("demo_resumed", f"Resumed at step {self.demo_step}")
        return {"status": "resumed", "step": self.demo_step}

    def increase_rainfall(self) -> Dict:
        """Increase rainfall intensity for demo."""
        self.rainfall_multiplier = min(self.rainfall_multiplier + 2.0, 15.0)
        self.base_rainfall_mm = min(self.base_rainfall_mm + 15, 120)
        self.water_level_base = min(self.water_level_base + 0.5, 8.0)
        self.soil_moisture_base = min(self.soil_moisture_base + 8, 98)
        self.tick()

        self._log_event("rainfall_increased", f"Rainfall multiplier: {self.rainfall_multiplier}x")
        return {
            "rainfall_multiplier": self.rainfall_multiplier,
            "base_rainfall_mm": self.base_rainfall_mm,
            "water_level_base": self.water_level_base,
            "soil_moisture_base": self.soil_moisture_base,
            "message": f"Rainfall increased — now {self.base_rainfall_mm}mm, "
                       f"water level {self.water_level_base}m",
        }

    def fail_sensor(self, sensor_id: str = "sensor-water-02") -> Dict:
        """Inject sensor failure."""
        self._log_event("sensor_failure", f"Sensor {sensor_id} set to OFFLINE")
        return {
            "sensor_id": sensor_id,
            "scenario": "OFFLINE",
            "message": f"Sensor {sensor_id} is now OFFLINE",
        }

    def close_road(self, road_id: str = "road-bridge") -> Dict:
        """Close a road."""
        self.road_overrides[road_id] = "CLOSED"
        self._log_event("road_closed", f"Road {road_id} closed")
        return {
            "road_id": road_id,
            "status": "CLOSED",
            "message": f"Road {road_id} is now CLOSED",
        }

    def degrade_network(self) -> Dict:
        """Simulate network degradation."""
        self.network_status = NetworkStatus.DEGRADED
        self._log_event("network_degraded", "Network status: DEGRADED")
        return {
            "network_status": "DEGRADED",
            "message": "Network is now DEGRADED — some data may be stale",
        }

    def restore_network(self) -> Dict:
        """Restore network to ONLINE."""
        self.network_status = NetworkStatus.ONLINE
        self._log_event("network_restored", "Network status: ONLINE")
        return {"network_status": "ONLINE", "message": "Network restored"}

    # -----------------------------------------------------------------------
    # Sensor Data Generation
    # -----------------------------------------------------------------------

    def get_sensor_overrides(self) -> Dict[str, Dict]:
        """Get current sensor data based on demo state."""
        from app.data import SENSORS, get_normal_readings
        import random

        readings = get_normal_readings()
        now = datetime.now(timezone.utc)

        for sid, reading in readings.items():
            reading["timestamp"] = now

            if "rainfall_mm" in reading:
                reading["rainfall_mm"] = round(
                    max(0, self.base_rainfall_mm * (0.8 + random.random() * 0.4)), 1
                )

            if "water_level_m" in reading:
                reading["water_level_m"] = round(
                    max(0.5, self.water_level_base + random.gauss(0, 0.1)), 2
                )

            if "soil_moisture_percent" in reading:
                reading["soil_moisture_percent"] = round(
                    min(98, max(20, self.soil_moisture_base + random.gauss(0, 2))), 1
                )

        return readings

    # -----------------------------------------------------------------------
    # Simulation
    # -----------------------------------------------------------------------

    def run_simulation(self, request: SimulationRequest) -> SimulationResponse:
        """Run a deterministic scenario simulation."""
        timeline = []
        sim_id = f"sim-{uuid.uuid4().hex[:8]}"

        # Generate timeline based on scenario
        scenario_profiles = self._get_scenario_profile(request.scenario)

        peak_risk = RiskLevel.NORMAL
        peak_time = 0

        for i, t in enumerate(range(0, request.duration_minutes + 1, 5)):
            profile = scenario_profiles(t, request)

            risk_level = self._prob_to_level(profile["risk_probability"])
            if self._risk_severity(risk_level) > self._risk_severity(peak_risk):
                peak_risk = risk_level
                peak_time = t

            timeline.append(SimulationTimelinePoint(
                time_offset_minutes=t,
                rainfall_mm=profile["rainfall_mm"],
                water_level_m=profile["water_level_m"],
                soil_moisture_percent=profile["soil_moisture_percent"],
                risk_level=risk_level,
                risk_probability=profile["risk_probability"],
                roads_threatened=profile.get("roads_threatened", 0),
                shelters_affected=profile.get("shelters_affected", 0),
                departure_window_minutes=profile.get("departure_window"),
            ))

        self._log_event("simulation_run", f"Scenario: {request.scenario.value}")

        return SimulationResponse(
            simulation_id=sim_id,
            scenario=request.scenario.value,
            timeline=timeline,
            peak_risk=peak_risk,
            peak_time_minutes=peak_time,
            total_duration_minutes=request.duration_minutes,
            timestamp=datetime.now(timezone.utc),
            note="DEMO SIMULATION — synthetic data only",
        )

    def _get_scenario_profile(self, scenario: DemoScenario):
        """Return a function that generates parameters at each timestep."""
        import math

        def normal(t, req):
            return {
                "rainfall_mm": 5 + 2 * math.sin(t / 10),
                "water_level_m": 2.0 + 0.1 * math.sin(t / 15),
                "soil_moisture_percent": 42 + 3 * math.sin(t / 20),
                "risk_probability": 0.05 + 0.02 * math.sin(t / 10),
            }

        def flash_flood(t, req):
            # Rapid escalation peaking at ~40 minutes
            phase = min(t / 40, 1.0)
            decline = max(0, (t - 45) / 15) if t > 45 else 0
            intensity = phase * (1 - decline * 0.5)

            rain = req.rainfall_intensity * intensity
            wl = 2.0 + (req.water_level - 2.0) * intensity
            sm = 42 + (req.soil_moisture - 42) * intensity
            risk = min(0.95, 0.05 + 0.85 * intensity)

            threatened = int(3 * intensity)
            shelters_hit = 1 if intensity > 0.7 else 0
            departure = max(0, 45 - t * 1.2) if risk > 0.3 else None

            return {
                "rainfall_mm": round(rain, 1),
                "water_level_m": round(wl, 2),
                "soil_moisture_percent": round(sm, 1),
                "risk_probability": round(risk, 3),
                "roads_threatened": threatened,
                "shelters_affected": shelters_hit,
                "departure_window": round(departure, 1) if departure else None,
            }

        def landslide_cascade(t, req):
            phase = min(t / 35, 1.0)
            decline = max(0, (t - 50) / 20) if t > 50 else 0
            intensity = phase * (1 - decline * 0.3)

            return {
                "rainfall_mm": round(req.rainfall_intensity * 1.2 * intensity, 1),
                "water_level_m": round(2.0 + 4.0 * intensity, 2),
                "soil_moisture_percent": round(min(98, 42 + 50 * intensity), 1),
                "risk_probability": round(min(0.98, 0.05 + 0.9 * intensity), 3),
                "roads_threatened": int(4 * intensity),
                "shelters_affected": int(2 * intensity),
                "departure_window": round(max(0, 35 - t * 1.0), 1) if intensity > 0.3 else None,
            }

        def watch_scenario(t, req):
            intensity = min(t / 60, 0.45)
            return {
                "rainfall_mm": round(20 + 15 * intensity, 1),
                "water_level_m": round(2.0 + 1.0 * intensity, 2),
                "soil_moisture_percent": round(50 + 15 * intensity, 1),
                "risk_probability": round(0.15 + 0.25 * intensity, 3),
                "roads_threatened": 1 if intensity > 0.3 else 0,
            }

        def warning_scenario(t, req):
            intensity = min(t / 45, 0.7)
            return {
                "rainfall_mm": round(40 + 30 * intensity, 1),
                "water_level_m": round(2.5 + 2.0 * intensity, 2),
                "soil_moisture_percent": round(60 + 25 * intensity, 1),
                "risk_probability": round(0.35 + 0.4 * intensity, 3),
                "roads_threatened": int(2 * intensity),
                "departure_window": round(max(5, 30 - t * 0.6), 1) if intensity > 0.3 else None,
            }

        scenarios = {
            DemoScenario.NORMAL: normal,
            DemoScenario.FLASH_FLOOD: flash_flood,
            DemoScenario.LANDSLIDE_CASCADE: landslide_cascade,
            DemoScenario.WATCH: watch_scenario,
            DemoScenario.WARNING: warning_scenario,
            DemoScenario.SENSOR_FAILURE: normal,  # Same as normal but sensor fails
            DemoScenario.NETWORK_FAILURE: normal,
            DemoScenario.NEAR_MISS: watch_scenario,
        }
        return scenarios.get(scenario, normal)

    def _prob_to_level(self, prob: float) -> RiskLevel:
        from app.config import settings
        if prob >= settings.RISK_THRESHOLD_CRITICAL:
            return RiskLevel.CRITICAL
        elif prob >= settings.RISK_THRESHOLD_EVACUATE:
            return RiskLevel.EVACUATE
        elif prob >= settings.RISK_THRESHOLD_WARNING:
            return RiskLevel.WARNING
        elif prob >= settings.RISK_THRESHOLD_WATCH:
            return RiskLevel.WATCH
        elif prob >= settings.RISK_THRESHOLD_AWARENESS:
            return RiskLevel.AWARENESS
        return RiskLevel.NORMAL

    def _risk_severity(self, level: RiskLevel) -> int:
        return {
            RiskLevel.NORMAL: 0, RiskLevel.AWARENESS: 1, RiskLevel.WATCH: 2,
            RiskLevel.WARNING: 3, RiskLevel.EVACUATE: 4, RiskLevel.CRITICAL: 5,
        }.get(level, 0)

    def _log_event(self, event_type: str, description: str):
        self.demo_events.append({
            "type": event_type,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step": self.demo_step,
        })

    def get_events(self) -> List[Dict]:
        return list(self.demo_events)


# Singleton
demo_controller = DemoController()
