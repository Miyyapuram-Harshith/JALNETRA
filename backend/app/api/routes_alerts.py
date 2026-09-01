"""
JALNETRA API — Alert & WhatsApp Routes
"""

from fastapi import APIRouter
from datetime import datetime, timezone

from app.schemas import (
    AlertCreate, AlertInfo, AlertResponse, AlertType, AlertChannel,
    WhatsAppAlertRequest, WhatsAppStatus, RiskLevel,
)
from app.services.alert_service import alert_service
from app.services.audit_service import audit_service
from app.providers.whatsapp import get_whatsapp_provider
from app.config import settings
from app.simulation.demo_controller import demo_controller
from app.engines.risk_engine import risk_engine
from app.engines.safe_departure import safe_departure_engine
from app.realtime.websocket_manager import ws_manager
from app.utils import JalnetraError, ErrorCode

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

# WhatsApp provider (initialized from config)
_whatsapp = get_whatsapp_provider(
    provider_type=settings.WHATSAPP_PROVIDER,
    access_token=settings.WHATSAPP_ACCESS_TOKEN,
    phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
    default_recipient=settings.WHATSAPP_RECIPIENT_NUMBER,
)


@router.get("", response_model=AlertResponse)
async def get_alerts():
    """Get alert history."""
    alerts = alert_service.get_alerts()
    return AlertResponse(
        alerts=alerts,
        total=len(alerts),
        timestamp=datetime.now(timezone.utc),
    )


@router.post("", response_model=AlertInfo)
async def create_alert(data: AlertCreate):
    """Create a new alert."""
    # Get current risk for context
    sensor_data = demo_controller.get_sensor_overrides()
    weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}
    risk_response = risk_engine.assess_all_zones(sensor_data, weather_data)
    max_risk = max(risk_response.zones, key=lambda z: z.risk_probability)

    # Get departure data
    departure = safe_departure_engine.calculate(
        hazard_arrival_minutes=max_risk.estimated_onset_minutes or 60.0,
        road_statuses=demo_controller.road_overrides,
        risk_probability=max_risk.risk_probability,
        confidence_score=max_risk.confidence_score,
    )

    alert = alert_service.create_alert(
        zone_id=data.zone_id,
        alert_type=data.alert_type,
        risk_level=max_risk.risk_level,
        channel=data.channel,
        language=data.language,
        recipient=data.recipient,
        risk_data={
            "estimated_onset_minutes": max_risk.estimated_onset_minutes,
            "confidence": max_risk.confidence.value,
        },
        departure_data={
            "safe_departure_window_minutes": departure.safe_departure_window_minutes,
            "recommended_shelter_name": departure.recommended_shelter_name,
            "recommended_route_name": departure.recommended_route.route_name if departure.recommended_route else "N/A",
        },
    )

    await ws_manager.broadcast("alerts", "ALERT_ISSUED", {
        "alert_id": alert.alert_id,
        "alert_type": alert.alert_type.value,
        "risk_level": alert.risk_level.value,
        "zone_id": alert.zone_id,
    })

    audit_service.log("authority", "alert_created", new_state={
        "alert_id": alert.alert_id, "type": alert.alert_type.value,
    })

    return alert


@router.post("/whatsapp")
async def send_whatsapp_alert(request: WhatsAppAlertRequest):
    """
    Send a WhatsApp alert.

    1. Validates/creates alert
    2. Renders multilingual message
    3. Sends through configured provider (mock or meta)
    4. Stores provider response
    5. Returns status

    If WHATSAPP_PROVIDER=mock: returns DEMO_MESSAGE_GENERATED
    If WHATSAPP_PROVIDER=meta with valid credentials: sends real WhatsApp message
    """
    # Get or create alert
    alert = None
    if request.alert_id:
        alert = alert_service.get_alert_by_id(request.alert_id)

    if not alert:
        # Create new alert
        sensor_data = demo_controller.get_sensor_overrides()
        weather_data = {"forecast_rainfall_mm": demo_controller.base_rainfall_mm * 1.5}
        risk_response = risk_engine.assess_all_zones(sensor_data, weather_data)
        max_risk = max(risk_response.zones, key=lambda z: z.risk_probability)

        departure = safe_departure_engine.calculate(
            hazard_arrival_minutes=max_risk.estimated_onset_minutes or 60.0,
            road_statuses=demo_controller.road_overrides,
            risk_probability=max_risk.risk_probability,
            confidence_score=max_risk.confidence_score,
        )

        alert = alert_service.create_alert(
            zone_id=request.zone_id,
            alert_type=request.alert_type,
            risk_level=max_risk.risk_level,
            channel=AlertChannel.WHATSAPP,
            language=request.language,
            recipient=request.recipient,
            risk_data={
                "estimated_onset_minutes": max_risk.estimated_onset_minutes,
                "confidence": max_risk.confidence.value,
            },
            departure_data={
                "safe_departure_window_minutes": departure.safe_departure_window_minutes,
                "recommended_shelter_name": departure.recommended_shelter_name,
                "recommended_route_name": departure.recommended_route.route_name if departure.recommended_route else "N/A",
            },
        )

    # Send through WhatsApp provider
    result = await _whatsapp.send_message(
        recipient=request.recipient or settings.WHATSAPP_RECIPIENT_NUMBER or "demo",
        message=alert.message,
    )

    # Update alert status
    status = WhatsAppStatus(result["status"])
    alert_service.update_alert_status(alert.alert_id, status, result)

    await ws_manager.broadcast("alerts", "WHATSAPP_SENT", {
        "alert_id": alert.alert_id,
        "status": result["status"],
        "provider": result.get("provider", "unknown"),
    })

    audit_service.log("system", "whatsapp_sent", new_state={
        "alert_id": alert.alert_id,
        "status": result["status"],
        "provider": result.get("provider"),
    })

    return {
        "alert_id": alert.alert_id,
        "message": alert.message,
        "whatsapp_status": result["status"],
        "provider": result.get("provider", "mock"),
        "message_id": result.get("message_id"),
        "is_demo": settings.DEMO_MODE or settings.WHATSAPP_PROVIDER == "mock",
        "details": result.get("details", {}),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
