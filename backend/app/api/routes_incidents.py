"""
JALNETRA API — Incident Routes
"""

from fastapi import APIRouter
from datetime import datetime, timezone

from app.schemas import (
    IncidentInfo, IncidentCreate, IncidentUpdate, IncidentResponse,
    SOSRequest, IncidentStatus,
)
from app.services.incident_service import incident_service
from app.services.audit_service import audit_service
from app.realtime.websocket_manager import ws_manager
from app.utils import JalnetraError, ErrorCode

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


@router.get("", response_model=IncidentResponse)
async def get_incidents():
    """Get all incidents, newest first."""
    incidents = incident_service.get_all()
    return IncidentResponse(
        incidents=incidents,
        total=len(incidents),
        timestamp=datetime.now(timezone.utc),
    )


@router.post("", response_model=IncidentInfo)
async def create_incident(data: IncidentCreate):
    """Create a new incident from authority/system."""
    incident = incident_service.create_incident(data)

    await ws_manager.broadcast("incidents", "INCIDENT_CREATED", {
        "incident_id": incident.id,
        "priority": incident.priority.value,
        "location": incident.location,
    })

    audit_service.log("authority", "incident_created", new_state={
        "incident_id": incident.id, "priority": incident.priority.value,
    })

    return incident


@router.post("/sos", response_model=IncidentInfo)
async def citizen_sos(sos: SOSRequest):
    """
    Citizen SOS — create an emergency incident.

    Creates an incident and notifies authority/responder through the realtime system.

    Note: This is a DEMO system. It does NOT dispatch actual emergency services
    unless a real integration exists.
    """
    incident = incident_service.create_from_sos(sos)

    await ws_manager.broadcast("incidents", "INCIDENT_CREATED", {
        "incident_id": incident.id,
        "priority": incident.priority.value,
        "source": "sos",
        "location": incident.location,
        "people_affected": incident.people_affected,
    })

    audit_service.log("citizen", "sos_triggered", new_state={
        "incident_id": incident.id,
        "location": incident.location,
    })

    return incident


@router.patch("/{incident_id}", response_model=IncidentInfo)
async def update_incident(incident_id: str, update: IncidentUpdate):
    """Update incident status or assignment."""
    incident = incident_service.update_incident(incident_id, update)
    if not incident:
        raise JalnetraError(404, ErrorCode.INCIDENT_NOT_FOUND, f"Incident {incident_id} not found")

    await ws_manager.broadcast("incidents", "INCIDENT_UPDATED", {
        "incident_id": incident.id,
        "status": incident.status.value,
        "assigned_responder": incident.assigned_responder,
    })

    audit_service.log("system", "incident_updated", new_state={
        "incident_id": incident.id,
        "status": incident.status.value,
    })

    return incident
