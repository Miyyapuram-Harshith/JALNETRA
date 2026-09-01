"""
JALNETRA Impact Engine
======================
Intersects predicted flood hazard with infrastructure to determine
affected roads, shelters, settlements, and population.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from shapely.geometry import shape, Point, LineString
from shapely.ops import unary_union

from app.data import ROADS, SHELTERS, ZONES, CRITICAL_INFRASTRUCTURE
from app.schemas import (
    ImpactResponse, AffectedFacility, RoadStatus, DataFreshness,
)


class ImpactEngine:
    """
    Spatial impact analysis engine.

    Intersects predicted flood extent with:
    - Roads → threatened road list with arrival times
    - Shelters → accessibility status changes
    - Settlements → affected population estimates
    - Critical infrastructure → hospitals, bridges at risk
    """

    def __init__(self):
        # Pre-parse geometries
        self._road_geometries = {}
        for road in ROADS:
            try:
                geom = shape(road["geometry"])
                self._road_geometries[road["road_id"]] = {
                    "geometry": geom,
                    "data": road,
                }
            except Exception:
                pass

        self._zone_geometries = {}
        for zone in ZONES:
            try:
                geom = shape(zone["geojson"]["geometry"])
                self._zone_geometries[zone["zone_id"]] = {
                    "geometry": geom,
                    "data": zone,
                }
            except Exception:
                pass

    def assess_impact(
        self,
        hazard_geometry: Optional[Dict] = None,
        hazard_arrival_minutes: Optional[float] = None,
        risk_probability: float = 0.0,
    ) -> ImpactResponse:
        """
        Assess impact of predicted flood hazard on infrastructure.

        Args:
            hazard_geometry: GeoJSON geometry of predicted flood extent
            hazard_arrival_minutes: Estimated minutes until hazard arrival
            risk_probability: Current risk probability (0-1)

        Returns:
            ImpactResponse with affected areas and facilities
        """
        threatened_roads = []
        threatened_facilities = []
        isolated_zones = []
        affected_population = 0
        affected_area_km2 = 0.0

        hazard_geom = None
        if hazard_geometry:
            try:
                hazard_geom = shape(hazard_geometry)
                # Approximate area
                affected_area_km2 = hazard_geom.area * 111 * 96
            except Exception:
                hazard_geom = None

        # --- Road Impact ---
        for road_id, road_info in self._road_geometries.items():
            road_data = road_info["data"]
            road_geom = road_info["geometry"]

            status = RoadStatus.SAFE
            road_arrival = None

            if hazard_geom and not hazard_geom.is_empty:
                if road_geom.intersects(hazard_geom):
                    # Road intersects hazard zone
                    intersection_ratio = (
                        road_geom.intersection(hazard_geom).length / road_geom.length
                        if road_geom.length > 0 else 0
                    )

                    if intersection_ratio > 0.5:
                        status = RoadStatus.UNSAFE
                    elif intersection_ratio > 0.1:
                        status = RoadStatus.THREATENED
                    else:
                        status = RoadStatus.THREATENED

                    road_arrival = hazard_arrival_minutes

                elif road_data.get("flood_vulnerable", False) and risk_probability > 0.4:
                    status = RoadStatus.THREATENED
                    road_arrival = (hazard_arrival_minutes or 60) * 1.5

            elif road_data.get("flood_vulnerable", False) and risk_probability > 0.6:
                status = RoadStatus.THREATENED

            threatened_roads.append({
                "road_id": road_id,
                "name": road_data["name"],
                "type": road_data["type"],
                "current_status": status.value,
                "predicted_hazard_arrival_minutes": round(road_arrival, 1) if road_arrival else None,
                "risk": "HIGH" if status in [RoadStatus.UNSAFE, RoadStatus.CLOSED] else
                        "MEDIUM" if status == RoadStatus.THREATENED else "LOW",
            })

        # --- Zone/Population Impact ---
        for zone_id, zone_info in self._zone_geometries.items():
            zone_data = zone_info["data"]
            zone_geom = zone_info["geometry"]

            if hazard_geom and not hazard_geom.is_empty and zone_geom.intersects(hazard_geom):
                intersection_area = zone_geom.intersection(hazard_geom).area
                zone_area = zone_geom.area if zone_geom.area > 0 else 1
                affected_ratio = min(intersection_area / zone_area, 1.0)

                zone_pop = zone_data.get("population", 0)
                affected_population += int(zone_pop * affected_ratio)

                # Check if zone is isolated (all access roads threatened)
                unsafe_roads = [r for r in threatened_roads
                                if r["current_status"] in ["UNSAFE", "CLOSED"]]
                if len(unsafe_roads) >= len(threatened_roads) * 0.5 and risk_probability > 0.5:
                    isolated_zones.append(zone_id)

        # --- Facility Impact ---
        for shelter in SHELTERS:
            shelter_point = Point(shelter["location"]["lon"], shelter["location"]["lat"])

            if hazard_geom and not hazard_geom.is_empty and hazard_geom.contains(shelter_point):
                status = "INACCESSIBLE"
            elif risk_probability > 0.6 and shelter.get("elevation_m", 1000) < 900:
                status = "THREATENED"
            else:
                status = "ACCESSIBLE"

            threatened_facilities.append(AffectedFacility(
                id=shelter["shelter_id"],
                name=shelter["name"],
                type="shelter",
                status=status,
                hazard_arrival_minutes=hazard_arrival_minutes if status != "ACCESSIBLE" else None,
                location=shelter["location"],
            ))

        for infra in CRITICAL_INFRASTRUCTURE:
            infra_point = Point(infra["location"]["lon"], infra["location"]["lat"])

            if hazard_geom and not hazard_geom.is_empty and hazard_geom.contains(infra_point):
                status = "AT_RISK"
            elif risk_probability > 0.5 and infra.get("elevation_m", 1000) < 900:
                status = "POTENTIALLY_AFFECTED"
            else:
                status = "SAFE"

            threatened_facilities.append(AffectedFacility(
                id=infra["id"],
                name=infra["name"],
                type=infra["type"],
                status=status,
                hazard_arrival_minutes=hazard_arrival_minutes if status != "SAFE" else None,
                location=infra["location"],
            ))

        now = datetime.now(timezone.utc)
        return ImpactResponse(
            affected_area_km2=round(affected_area_km2, 4),
            affected_population_estimate=affected_population,
            population_note="Modeled estimate based on aggregated zone data",
            threatened_roads=threatened_roads,
            threatened_facilities=threatened_facilities,
            isolated_zones=isolated_zones,
            timestamp=now,
            freshness=DataFreshness(
                timestamp=now, age_seconds=0, quality="modeled", source="demo"
            ),
        )


# Singleton
impact_engine = ImpactEngine()
