"""
JALNETRA Incident Service
=========================
Incident management: create from SOS, priority calculation, status transitions,
responder assignment. Does NOT claim actual emergency-service dispatch.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
import uuid
import logging

from app.data import RESPONDERS
from app.schemas import (
    IncidentInfo, IncidentStatus, IncidentPriority,
    SOSRequest, IncidentCreate, IncidentUpdate,
)

logger = logging.getLogger("jalnetra.incident_service")


class IncidentService:
    """Incident management with priority calculation and responder assignment."""

    def __init__(self):
        self._incidents: List[IncidentInfo] = []
        self._responder_assignments: Dict[str, str] = {}  # responder_id -> incident_id

    def create_from_sos(self, sos: SOSRequest) -> IncidentInfo:
        """Create incident from citizen SOS."""
        priority = self._calculate_priority(
            people_affected=sos.people_count,
            medical_needed=sos.medical_needed,
        )

        incident_id = f"incident-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        incident = IncidentInfo(
            id=incident_id,
            location={"lat": sos.latitude, "lon": sos.longitude},
            priority=priority,
            severity="high" if sos.medical_needed else "moderate",
            people_affected=sos.people_count,
            hazard_arrival_minutes=None,
            recommended_route=None,
            status=IncidentStatus.NEW,
            assigned_responder=None,
            created_at=now,
            updated_at=now,
            source="sos",
        )

        self._incidents.append(incident)
        logger.info(f"SOS incident created: {incident_id} at ({sos.latitude}, {sos.longitude})")

        # Auto-assign nearest available responder
        self._auto_assign(incident)

        return incident

    def create_incident(self, data: IncidentCreate) -> IncidentInfo:
        """Create incident from authority/system."""
        priority = data.priority or self._calculate_priority(
            people_affected=data.people_affected,
            medical_needed=data.medical_needed,
        )

        incident_id = f"incident-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        incident = IncidentInfo(
            id=incident_id,
            location={"lat": data.location_lat, "lon": data.location_lon},
            priority=priority,
            severity=data.severity,
            people_affected=data.people_affected,
            status=IncidentStatus.NEW,
            created_at=now,
            updated_at=now,
            source="manual",
        )

        self._incidents.append(incident)
        logger.info(f"Incident created: {incident_id}")
        return incident

    def update_incident(self, incident_id: str, update: IncidentUpdate) -> Optional[IncidentInfo]:
        """Update incident status/assignment."""
        incident = self.get_by_id(incident_id)
        if not incident:
            return None

        if update.status:
            incident.status = update.status
        if update.assigned_responder:
            incident.assigned_responder = update.assigned_responder
        if update.priority:
            incident.priority = update.priority

        incident.updated_at = datetime.now(timezone.utc)

        logger.info(f"Incident {incident_id} updated: status={incident.status}")
        return incident

    def get_all(self, limit: int = 50) -> List[IncidentInfo]:
        """Get all incidents, newest first."""
        return sorted(self._incidents, key=lambda i: i.created_at, reverse=True)[:limit]

    def get_by_id(self, incident_id: str) -> Optional[IncidentInfo]:
        return next((i for i in self._incidents if i.id == incident_id), None)

    def get_active(self) -> List[IncidentInfo]:
        """Get active (non-resolved) incidents."""
        return [
            i for i in self._incidents
            if i.status != IncidentStatus.RESOLVED
        ]

    def _calculate_priority(
        self,
        people_affected: int = 1,
        medical_needed: bool = False,
        hazard_arrival_minutes: Optional[float] = None,
        route_accessible: bool = True,
        isolation: bool = False,
    ) -> IncidentPriority:
        """
        Calculate priority using:
        urgency, people affected, hazard arrival, route accessibility,
        medical need, isolation.
        """
        score = 0

        # People affected
        if people_affected >= 10:
            score += 3
        elif people_affected >= 5:
            score += 2
        elif people_affected >= 2:
            score += 1

        # Medical need
        if medical_needed:
            score += 2

        # Hazard proximity
        if hazard_arrival_minutes is not None:
            if hazard_arrival_minutes < 10:
                score += 3
            elif hazard_arrival_minutes < 20:
                score += 2
            elif hazard_arrival_minutes < 30:
                score += 1

        # Route accessibility
        if not route_accessible:
            score += 2

        # Isolation
        if isolation:
            score += 2

        # Map to priority
        if score >= 7:
            return IncidentPriority.CRITICAL
        elif score >= 4:
            return IncidentPriority.HIGH
        elif score >= 2:
            return IncidentPriority.MEDIUM
        else:
            return IncidentPriority.LOW

    def _auto_assign(self, incident: IncidentInfo):
        """Auto-assign the nearest available responder."""
        available = [
            r for r in RESPONDERS
            if r["responder_id"] not in self._responder_assignments
            and r["status"] == "AVAILABLE"
        ]

        if available:
            # Simple nearest assignment (could use distance calculation)
            responder = available[0]
            incident.assigned_responder = responder["responder_id"]
            incident.status = IncidentStatus.ASSIGNED
            self._responder_assignments[responder["responder_id"]] = incident.id
            logger.info(f"Auto-assigned {responder['responder_id']} to {incident.id}")

    def reset(self):
        """Reset all incidents."""
        self._incidents.clear()
        self._responder_assignments.clear()


# Singleton
incident_service = IncidentService()
