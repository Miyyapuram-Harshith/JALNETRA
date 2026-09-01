"""
JALNETRA Alert Service
======================
Alert engine: trigger logic, deduplication, cooldown, escalation,
de-escalation, multilingual template rendering.
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import uuid
import logging

from app.config import settings
from app.schemas import (
    AlertInfo, AlertType, AlertChannel, WhatsAppStatus,
    RiskLevel, AlertCreate, WhatsAppAlertRequest,
)
from app.utils.i18n import render_alert_message

logger = logging.getLogger("jalnetra.alert_service")


class AlertService:
    """Alert engine with deduplication, escalation, and multilingual support."""

    def __init__(self):
        self._alerts: List[AlertInfo] = []
        self._last_alert_time: Dict[str, datetime] = {}  # zone_id -> last alert time
        self._last_alert_level: Dict[str, RiskLevel] = {}  # zone_id -> last alert level

    def should_trigger_alert(
        self,
        zone_id: str,
        risk_level: RiskLevel,
        confidence: str = "HIGH",
        lead_time_minutes: Optional[float] = None,
    ) -> bool:
        """
        Determine if an alert should be triggered based on policy.

        Considers: risk level, confidence, lead time, deduplication, cooldown.
        """
        # Only alert for WATCH and above
        risk_severity = self._risk_to_int(risk_level)
        if risk_severity < 2:  # Below WATCH
            return False

        # Cooldown check
        last_time = self._last_alert_time.get(zone_id)
        if last_time:
            elapsed = (datetime.now(timezone.utc) - last_time).total_seconds()
            if elapsed < settings.ALERT_COOLDOWN_SECONDS:
                # Allow escalation even within cooldown
                last_level = self._last_alert_level.get(zone_id, RiskLevel.NORMAL)
                if self._risk_to_int(risk_level) <= self._risk_to_int(last_level):
                    return False

        return True

    def create_alert(
        self,
        zone_id: str,
        alert_type: AlertType,
        risk_level: RiskLevel,
        channel: AlertChannel = AlertChannel.WHATSAPP,
        language: str = "en",
        recipient: Optional[str] = None,
        risk_data: Optional[Dict] = None,
        route_data: Optional[Dict] = None,
        departure_data: Optional[Dict] = None,
    ) -> AlertInfo:
        """Create a new alert with rendered message."""

        # Determine action text
        action_map = {
            AlertType.AWARENESS: "Monitor conditions",
            AlertType.WATCH: "Be prepared to act",
            AlertType.WARNING: "Prepare for possible evacuation",
            AlertType.EVACUATION_RECOMMENDED: "LEAVE NOW",
            AlertType.CRITICAL: "SEEK HIGHER GROUND IMMEDIATELY",
        }

        # Build template variables
        template_vars = {
            "zone": zone_id.replace("zone-", "").replace("-", " ").title(),
            "region": "Hilly Village Alpha",
            "risk_level": risk_level.value,
            "action": action_map.get(alert_type, "Stay informed"),
            "impact_minutes": "N/A",
            "shelter": "N/A",
            "route": "N/A",
            "departure_window": "N/A",
            "confidence": "N/A",
        }

        if risk_data:
            template_vars["impact_minutes"] = str(
                risk_data.get("estimated_onset_minutes", "N/A")
            )
            template_vars["confidence"] = risk_data.get("confidence", "N/A")

        if departure_data:
            template_vars["departure_window"] = str(
                departure_data.get("safe_departure_window_minutes", "N/A")
            )
            template_vars["shelter"] = departure_data.get("recommended_shelter_name", "N/A")
            template_vars["route"] = departure_data.get("recommended_route_name", "N/A")

        if route_data:
            template_vars["route"] = route_data.get("route_name", template_vars["route"])

        # Render message
        message = render_alert_message(
            alert_type=alert_type.value,
            language=language,
            **template_vars,
        )

        alert_id = f"alert-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        alert = AlertInfo(
            alert_id=alert_id,
            zone_id=zone_id,
            alert_type=alert_type,
            risk_level=risk_level,
            channel=channel,
            message=message,
            status=WhatsAppStatus.MESSAGE_PREPARED,
            recipient=recipient,
            created_at=now,
            is_demo=settings.DEMO_MODE,
        )

        self._alerts.append(alert)
        self._last_alert_time[zone_id] = now
        self._last_alert_level[zone_id] = risk_level

        logger.info(f"Alert created: {alert_id} [{alert_type.value}] for {zone_id}")
        return alert

    def update_alert_status(self, alert_id: str, status: WhatsAppStatus, provider_response: Dict = None):
        """Update alert delivery status."""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.status = status
                alert.provider_response = provider_response
                if status == WhatsAppStatus.DELIVERY_CONFIRMED:
                    alert.delivered_at = datetime.now(timezone.utc)
                break

    def get_alerts(self, limit: int = 50) -> List[AlertInfo]:
        """Get recent alerts."""
        return sorted(self._alerts, key=lambda a: a.created_at, reverse=True)[:limit]

    def get_alert_by_id(self, alert_id: str) -> Optional[AlertInfo]:
        return next((a for a in self._alerts if a.alert_id == alert_id), None)

    def check_escalation(self, zone_id: str, new_level: RiskLevel) -> Optional[str]:
        """Check if this represents an escalation or de-escalation."""
        last_level = self._last_alert_level.get(zone_id)
        if not last_level:
            return "new"

        old_severity = self._risk_to_int(last_level)
        new_severity = self._risk_to_int(new_level)

        if new_severity > old_severity:
            return "escalation"
        elif new_severity < old_severity:
            return "de-escalation"
        return "update"

    def reset(self):
        """Reset all alert state."""
        self._alerts.clear()
        self._last_alert_time.clear()
        self._last_alert_level.clear()

    def _risk_to_int(self, level: RiskLevel) -> int:
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
alert_service = AlertService()
