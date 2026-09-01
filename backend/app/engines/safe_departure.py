"""
JALNETRA Safe Departure Engine
===============================
Central JALNETRA intelligence feature.

Calculates: hazard_arrival - travel_time - safety_buffer
with adjustments for route deterioration, uncertainty, and confidence.

Always labeled: MODELED ESTIMATE — not a guarantee of safety.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.config import settings
from app.engines.route_engine import route_engine
from app.schemas import (
    SafeDepartureWindow, ConfidenceLevel, RouteOption, DataFreshness,
)


class SafeDepartureEngine:
    """
    Calculates the safe departure window for evacuation.

    Formula:
        safe_departure_window = hazard_arrival - travel_time - safety_buffer

    Adjustments:
        - Route deterioration over time
        - Confidence/uncertainty scaling
        - Multiple candidate routes considered

    ALWAYS labeled as MODELED ESTIMATE.
    """

    def __init__(self):
        self._safety_buffer_minutes = settings.SAFETY_BUFFER_MINUTES

    def calculate(
        self,
        hazard_arrival_minutes: float,
        road_statuses: Dict[str, str] = None,
        hazard_arrivals: Dict[str, Optional[float]] = None,
        risk_probability: float = 0.5,
        confidence_score: float = 0.8,
        shelter_id: Optional[str] = None,
    ) -> SafeDepartureWindow:
        """
        Calculate safe departure window.

        Args:
            hazard_arrival_minutes: Estimated minutes until hazard arrives
            road_statuses: Current road status overrides
            hazard_arrivals: Per-road hazard arrival times
            risk_probability: Current risk probability
            confidence_score: Confidence in the prediction (0-1)
            shelter_id: Preferred shelter (optional)

        Returns:
            SafeDepartureWindow with all timing details
        """

        # Get best available route
        best_route = route_engine.get_best_route(
            road_statuses=road_statuses,
            hazard_arrivals=hazard_arrivals,
            risk_probability=risk_probability,
        )

        travel_time = best_route.total_travel_time_minutes if best_route else 15.0

        # --- Route deterioration adjustment ---
        # If route has threatened segments, add time buffer
        deterioration_factor = 1.0
        if best_route:
            from app.schemas import RoadStatus
            threatened_count = sum(
                1 for s in best_route.segments if s.status == RoadStatus.THREATENED
            )
            deterioration_factor = 1.0 + (threatened_count * 0.15)

        adjusted_travel_time = travel_time * deterioration_factor

        # --- Safety buffer with uncertainty scaling ---
        # Lower confidence = larger safety buffer
        uncertainty = 1.0 - confidence_score
        adjusted_buffer = self._safety_buffer_minutes * (1.0 + uncertainty * 0.5)

        # --- Safe departure window ---
        window = hazard_arrival_minutes - adjusted_travel_time - adjusted_buffer

        # Clamp to reasonable range
        window = max(0.0, window)

        # --- Confidence level ---
        if confidence_score >= 0.7:
            conf_level = ConfidenceLevel.HIGH
        elif confidence_score >= 0.4:
            conf_level = ConfidenceLevel.MEDIUM
        else:
            conf_level = ConfidenceLevel.LOW

        # --- Determine recommended shelter ---
        from app.data import SHELTERS
        recommended_shelter_id = None
        recommended_shelter_name = None

        if shelter_id:
            recommended_shelter_id = shelter_id
            shelter_data = next((s for s in SHELTERS if s["shelter_id"] == shelter_id), None)
            recommended_shelter_name = shelter_data["name"] if shelter_data else shelter_id
        elif best_route:
            # Find shelter from route definition
            for rd in route_engine.ROUTE_DEFINITIONS:
                if rd["route_id"] == best_route.route_id:
                    recommended_shelter_id = rd["destination_shelter"]
                    shelter_data = next(
                        (s for s in SHELTERS if s["shelter_id"] == recommended_shelter_id), None
                    )
                    recommended_shelter_name = shelter_data["name"] if shelter_data else recommended_shelter_id
                    break

        return SafeDepartureWindow(
            safe_departure_window_minutes=round(window, 1),
            hazard_arrival_minutes=round(hazard_arrival_minutes, 1),
            travel_time_minutes=round(adjusted_travel_time, 1),
            safety_buffer_minutes=round(adjusted_buffer, 1),
            confidence=conf_level,
            confidence_score=round(confidence_score, 3),
            uncertainty_minutes=round(uncertainty * 10, 1),
            recommended_route=best_route,
            recommended_shelter=recommended_shelter_id,
            recommended_shelter_name=recommended_shelter_name,
            note="MODELED ESTIMATE — not a guarantee of safety",
            timestamp=datetime.now(timezone.utc),
        )


# Singleton
safe_departure_engine = SafeDepartureEngine()
