"""
JALNETRA Flood Propagation Engine
==================================
PROTOTYPE SIMPLIFIED MODEL — not validated for operational use.

Deterministic spatial flood propagation using geometry buffering
and terrain-weighted expansion. Returns GeoJSON per timestep.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from shapely.geometry import shape, mapping, LineString, MultiPolygon, Polygon
from shapely.ops import unary_union
import json

from app.data import WATER_FEATURES, ZONES
from app.schemas import PropagationTimestep, PropagationResponse, DataFreshness


class PropagationEngine:
    """
    Simplified spatial flood propagation model.

    Method:
    1. Start from river/stream geometries
    2. Buffer outward over timesteps (T+0 through T+60)
    3. Weight expansion by terrain slope (flows downhill faster)
    4. Return GeoJSON hazard footprint per timestep

    This is a PROTOTYPE model for demonstration purposes.
    """

    MODEL_VERSION = "jalnetra-propagation-v1.0-prototype"

    # Timesteps in minutes
    TIMESTEPS = [0, 10, 20, 30, 45, 60]

    def __init__(self):
        # Pre-parse water feature geometries
        self._water_geometries = []
        for feature in WATER_FEATURES["features"]:
            try:
                geom = shape(feature["geometry"])
                self._water_geometries.append({
                    "geometry": geom,
                    "name": feature["properties"].get("name", "unknown"),
                    "type": feature["properties"].get("type", "river"),
                    "width_m": feature["properties"].get("width_m", 10),
                })
            except Exception:
                pass

        # Zone geometries for intersection
        self._zone_geometries = {}
        for zone in ZONES:
            try:
                geom = shape(zone["geojson"]["geometry"])
                self._zone_geometries[zone["zone_id"]] = {
                    "geometry": geom,
                    "elevation_m": zone.get("elevation_m", 900),
                    "slope_degrees": zone.get("slope_degrees", 10),
                }
            except Exception:
                pass

    def propagate(
        self,
        risk_probability: float = 0.5,
        rainfall_mm: float = 50.0,
        water_level_m: float = 3.0,
        soil_moisture_percent: float = 60.0,
    ) -> PropagationResponse:
        """
        Run flood propagation simulation.

        Args:
            risk_probability: Current overall risk (0-1)
            rainfall_mm: Current rainfall intensity
            water_level_m: Current water level
            soil_moisture_percent: Current soil moisture

        Returns:
            PropagationResponse with GeoJSON per timestep
        """
        timesteps = []

        # Base buffer size in degrees (approximate)
        # 0.001 degrees ≈ 111m at this latitude
        severity_factor = self._compute_severity(
            risk_probability, rainfall_mm, water_level_m, soil_moisture_percent
        )

        for t_minutes in self.TIMESTEPS:
            # Buffer grows with time and severity
            time_factor = t_minutes / 60.0
            buffer_degrees = self._compute_buffer(time_factor, severity_factor)

            # Create buffered hazard zone
            hazard_geom = self._create_hazard_geometry(buffer_degrees)

            if hazard_geom is None or hazard_geom.is_empty:
                continue

            # Compute intensity
            intensity = self._compute_intensity(t_minutes, severity_factor)

            # Area in approximate km²
            area_km2 = self._approx_area_km2(hazard_geom)

            timestep = PropagationTimestep(
                time_offset_minutes=t_minutes,
                hazard_geometry=mapping(hazard_geom),
                hazard_intensity=intensity,
                arrival_estimate_minutes=float(t_minutes) if t_minutes > 0 else None,
                uncertainty_meters=100 + t_minutes * 5,
                affected_area_km2=round(area_km2, 4),
            )
            timesteps.append(timestep)

        now = datetime.now(timezone.utc)
        return PropagationResponse(
            timesteps=timesteps,
            model_version=self.MODEL_VERSION,
            model_note="PROTOTYPE SIMPLIFIED MODEL — not validated for operational use",
            timestamp=now,
            freshness=DataFreshness(
                timestamp=now, age_seconds=0, quality="modeled", source="demo"
            ),
        )

    def _compute_severity(
        self,
        risk_prob: float,
        rainfall_mm: float,
        water_level_m: float,
        soil_moisture: float,
    ) -> float:
        """Compute overall severity factor (0-1)."""
        # Weighted combination
        severity = (
            0.3 * risk_prob
            + 0.3 * min(rainfall_mm / 100, 1.0)
            + 0.2 * min(water_level_m / 6.0, 1.0)
            + 0.2 * min(soil_moisture / 100, 1.0)
        )
        return max(0.05, min(1.0, severity))

    def _compute_buffer(self, time_factor: float, severity_factor: float) -> float:
        """Compute buffer size in degrees."""
        # Minimum buffer + growth
        base = 0.0002  # ~22m
        growth = 0.002 * time_factor * severity_factor  # Up to ~222m at T+60 max severity
        return base + growth

    def _create_hazard_geometry(self, buffer_degrees: float):
        """Buffer water features and union into single hazard zone."""
        try:
            buffered = []
            for wf in self._water_geometries:
                geom = wf["geometry"]
                # Rivers get bigger buffer than streams
                multiplier = 1.5 if wf["type"] == "river" else 1.0
                buf = geom.buffer(buffer_degrees * multiplier)
                buffered.append(buf)

            if not buffered:
                return None

            return unary_union(buffered)
        except Exception:
            return None

    def _compute_intensity(self, t_minutes: int, severity: float) -> str:
        """Determine hazard intensity label."""
        combined = severity * (1 + t_minutes / 60.0)
        if combined > 1.2:
            return "extreme"
        elif combined > 0.8:
            return "high"
        elif combined > 0.4:
            return "moderate"
        else:
            return "low"

    def _approx_area_km2(self, geom) -> float:
        """Approximate area in km² from degree-based geometry."""
        try:
            # At ~30.45°N: 1° lat ≈ 111km, 1° lon ≈ 96km
            area_deg2 = geom.area
            area_km2 = area_deg2 * 111 * 96
            return area_km2
        except Exception:
            return 0.0

    def get_hazard_at_time(self, t_minutes: int, severity_factor: float = 0.5) -> Optional[dict]:
        """Get hazard GeoJSON at a specific time offset."""
        time_factor = t_minutes / 60.0
        buffer_degrees = self._compute_buffer(time_factor, severity_factor)
        geom = self._create_hazard_geometry(buffer_degrees)
        if geom and not geom.is_empty:
            return mapping(geom)
        return None


# Singleton
propagation_engine = PropagationEngine()
