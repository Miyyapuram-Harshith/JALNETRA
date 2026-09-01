"""
JALNETRA Route Engine
=====================
Time-aware routing with hazard overlay.
A route safe now may become unsafe later.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from shapely.geometry import shape, LineString

from app.data import ROADS, SHELTERS, ZONES
from app.schemas import (
    RouteOption, RouteSegment, RoadStatus, RiskLevel,
    ConfidenceLevel, DataFreshness, RouteResponse,
)


class RouteEngine:
    """
    Time-aware route engine.

    Calculates travel time, overlays hazard arrival times,
    computes safety margins, and ranks candidate routes.
    """

    # Pre-defined route compositions (which roads form which routes)
    ROUTE_DEFINITIONS = [
        {
            "route_id": "route-A-highway",
            "name": "Route A — Main Highway to Shelter A",
            "segments": ["road-main-highway", "road-plateau"],
            "destination_shelter": "shelter-school",
        },
        {
            "route_id": "route-B-hillside",
            "name": "Route B — Hillside to Shelter B",
            "segments": ["road-hillside", "road-main-highway"],
            "destination_shelter": "shelter-community",
        },
        {
            "route_id": "route-C-direct",
            "name": "Route C — Direct Valley to Shelter A",
            "segments": ["road-valley-market", "road-plateau"],
            "destination_shelter": "shelter-school",
        },
        {
            "route_id": "route-D-bridge",
            "name": "Route D — Bridge Crossing to Shelter B",
            "segments": ["road-bridge", "road-valley-market"],
            "destination_shelter": "shelter-community",
        },
        {
            "route_id": "route-E-temple",
            "name": "Route E — Hillside to Temple Shelter",
            "segments": ["road-hillside"],
            "destination_shelter": "shelter-temple",
        },
    ]

    def __init__(self):
        self._road_index = {r["road_id"]: r for r in ROADS}
        self._shelter_index = {s["shelter_id"]: s for s in SHELTERS}

    def calculate_routes(
        self,
        road_statuses: Dict[str, str] = None,
        hazard_arrivals: Dict[str, Optional[float]] = None,
        risk_probability: float = 0.0,
    ) -> List[RouteOption]:
        """
        Calculate all available routes with risk assessment.

        Args:
            road_statuses: {road_id: status_string} overrides
            hazard_arrivals: {road_id: minutes_until_hazard}
            risk_probability: Overall risk probability

        Returns:
            List of RouteOption sorted by safety (safest first)
        """
        if road_statuses is None:
            road_statuses = {}
        if hazard_arrivals is None:
            hazard_arrivals = {}

        routes = []

        for route_def in self.ROUTE_DEFINITIONS:
            segments = []
            total_travel_time = 0.0
            total_distance = 0.0
            route_viable = True
            worst_segment_risk = RiskLevel.NORMAL
            min_safety_margin = float("inf")

            for road_id in route_def["segments"]:
                road = self._road_index.get(road_id)
                if not road:
                    continue

                # Get status (override or default)
                status_str = road_statuses.get(road_id, road.get("status", "SAFE"))
                try:
                    status = RoadStatus(status_str)
                except ValueError:
                    status = RoadStatus.SAFE

                # If road is closed, route is not viable
                if status == RoadStatus.CLOSED:
                    route_viable = False

                travel_time = road.get("travel_time_minutes", 5)
                total_travel_time += travel_time
                total_distance += road.get("length_km", 1.0)

                # Hazard arrival for this segment
                hazard_arrival = hazard_arrivals.get(road_id)

                # Safety margin
                safety_margin = None
                if hazard_arrival is not None:
                    # Time remaining when we reach this segment
                    safety_margin = hazard_arrival - total_travel_time
                    min_safety_margin = min(min_safety_margin, safety_margin)

                # Segment risk level
                seg_risk = self._segment_risk(status, safety_margin, risk_probability)
                if self._risk_severity(seg_risk) > self._risk_severity(worst_segment_risk):
                    worst_segment_risk = seg_risk

                segments.append(RouteSegment(
                    road_id=road_id,
                    road_name=road["name"],
                    status=status,
                    travel_time_minutes=travel_time,
                    hazard_arrival_minutes=hazard_arrival,
                    safety_margin_minutes=round(safety_margin, 1) if safety_margin is not None else None,
                ))

            if not route_viable:
                worst_segment_risk = RiskLevel.CRITICAL

            # Route confidence based on data quality
            confidence = ConfidenceLevel.HIGH
            if any(s.status == RoadStatus.THREATENED for s in segments):
                confidence = ConfidenceLevel.MEDIUM
            if any(s.status in [RoadStatus.UNSAFE, RoadStatus.CLOSED] for s in segments):
                confidence = ConfidenceLevel.LOW

            # Build route geometry from road geometries
            route_coords = []
            for road_id in route_def["segments"]:
                road = self._road_index.get(road_id)
                if road and "geometry" in road:
                    route_coords.extend(road["geometry"]["coordinates"])

            route_geometry = None
            if route_coords:
                route_geometry = {"type": "LineString", "coordinates": route_coords}

            routes.append(RouteOption(
                route_id=route_def["route_id"],
                route_name=route_def["name"],
                segments=segments,
                total_travel_time_minutes=round(total_travel_time, 1),
                total_distance_km=round(total_distance, 2),
                risk=worst_segment_risk,
                confidence=confidence,
                geometry=route_geometry,
            ))

        # Sort: safest first (lowest risk, then shortest travel time)
        routes.sort(key=lambda r: (self._risk_severity(r.risk), r.total_travel_time_minutes))

        return routes

    def get_best_route(
        self,
        road_statuses: Dict[str, str] = None,
        hazard_arrivals: Dict[str, Optional[float]] = None,
        risk_probability: float = 0.0,
    ) -> Optional[RouteOption]:
        """Get the safest viable route."""
        routes = self.calculate_routes(road_statuses, hazard_arrivals, risk_probability)
        # Filter out CRITICAL routes
        viable = [r for r in routes if r.risk != RiskLevel.CRITICAL]
        return viable[0] if viable else (routes[0] if routes else None)

    def get_route_to_shelter(
        self,
        shelter_id: str,
        road_statuses: Dict[str, str] = None,
        hazard_arrivals: Dict[str, Optional[float]] = None,
        risk_probability: float = 0.0,
    ) -> Optional[RouteOption]:
        """Get best route to a specific shelter."""
        routes = self.calculate_routes(road_statuses, hazard_arrivals, risk_probability)
        matching = [
            r for r in routes
            if any(rd["destination_shelter"] == shelter_id
                   for rd in self.ROUTE_DEFINITIONS if rd["route_id"] == r.route_id)
        ]
        return matching[0] if matching else None

    def _segment_risk(
        self,
        status: RoadStatus,
        safety_margin: Optional[float],
        risk_prob: float,
    ) -> RiskLevel:
        """Determine risk level for a road segment."""
        if status == RoadStatus.CLOSED:
            return RiskLevel.CRITICAL
        if status == RoadStatus.UNSAFE:
            return RiskLevel.EVACUATE

        if safety_margin is not None:
            if safety_margin < 0:
                return RiskLevel.CRITICAL
            elif safety_margin < 5:
                return RiskLevel.EVACUATE
            elif safety_margin < 15:
                return RiskLevel.WARNING
            elif safety_margin < 30:
                return RiskLevel.WATCH

        if status == RoadStatus.THREATENED:
            return RiskLevel.WATCH

        if risk_prob > 0.7:
            return RiskLevel.WARNING
        elif risk_prob > 0.4:
            return RiskLevel.AWARENESS

        return RiskLevel.NORMAL

    def _risk_severity(self, level: RiskLevel) -> int:
        """Numeric severity for sorting."""
        order = {
            RiskLevel.NORMAL: 0,
            RiskLevel.AWARENESS: 1,
            RiskLevel.WATCH: 2,
            RiskLevel.WARNING: 3,
            RiskLevel.EVACUATE: 4,
            RiskLevel.CRITICAL: 5,
        }
        return order.get(level, 0)


# Singleton
route_engine = RouteEngine()
