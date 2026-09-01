"""
JALNETRA WhatsApp Provider
===========================
WhatsAppProvider ABC with Mock and Meta implementations.
The alert engine does not depend directly on Meta/Twilio.

CREDENTIALS MUST REMAIN SERVER-SIDE.
Never expose through frontend APIs.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Optional
import logging
import uuid

from app.schemas import WhatsAppStatus

logger = logging.getLogger("jalnetra.whatsapp")


class WhatsAppProvider(ABC):
    """Abstract base for WhatsApp message sending."""

    @abstractmethod
    async def send_message(self, recipient: str, message: str) -> Dict:
        """
        Send a WhatsApp message.

        Returns:
            {
                "status": WhatsAppStatus value,
                "message_id": str,
                "provider": str,
                "timestamp": str,
                "details": dict
            }
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        pass


class MockWhatsAppProvider(WhatsAppProvider):
    """
    Mock provider for demo mode.
    Generates realistic mock message response without sending.
    """

    def __init__(self):
        self._messages: list = []

    async def send_message(self, recipient: str, message: str) -> Dict:
        msg_id = f"demo-wa-{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        result = {
            "status": WhatsAppStatus.DEMO_MESSAGE_GENERATED.value,
            "message_id": msg_id,
            "provider": "mock",
            "timestamp": now.isoformat(),
            "recipient": recipient or "demo-recipient",
            "message_preview": message[:200] + "..." if len(message) > 200 else message,
            "details": {
                "demo_mode": True,
                "note": "DEMO MODE — Message was not sent to WhatsApp. "
                       "Configure WHATSAPP_PROVIDER=meta with valid credentials to send real messages.",
            },
        }

        self._messages.append(result)
        logger.info(f"[DEMO] WhatsApp message generated: {msg_id}")
        logger.info(f"[DEMO] Message content:\n{message}")

        return result

    def is_configured(self) -> bool:
        return True  # Always "configured" in demo

    def get_sent_messages(self) -> list:
        return list(self._messages)

    def clear(self):
        self._messages.clear()


class MetaWhatsAppProvider(WhatsAppProvider):
    """
    Real Meta WhatsApp Business Cloud API provider.

    Uses the Meta Graph API to send template or text messages.
    Credentials remain server-side.
    """

    def __init__(self, access_token: str, phone_number_id: str, default_recipient: str = None):
        self._access_token = access_token
        self._phone_number_id = phone_number_id
        self._default_recipient = default_recipient
        self._api_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

    async def send_message(self, recipient: str, message: str) -> Dict:
        target = recipient or self._default_recipient
        if not target:
            return {
                "status": WhatsAppStatus.FAILED.value,
                "message_id": None,
                "provider": "meta",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": {"error": "No recipient number configured"},
            }

        try:
            import httpx

            payload = {
                "messaging_product": "whatsapp",
                "to": target,
                "type": "text",
                "text": {"body": message},
            }

            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            }

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self._api_url,
                    json=payload,
                    headers=headers,
                )

            if response.status_code == 200:
                data = response.json()
                msg_id = data.get("messages", [{}])[0].get("id", "unknown")
                logger.info(f"WhatsApp message sent successfully: {msg_id}")
                return {
                    "status": WhatsAppStatus.SENT.value,
                    "message_id": msg_id,
                    "provider": "meta",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {"response_status": response.status_code},
                }
            else:
                logger.error(f"WhatsApp API error: {response.status_code} - {response.text}")
                return {
                    "status": WhatsAppStatus.FAILED.value,
                    "message_id": None,
                    "provider": "meta",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": {
                        "error": f"API returned {response.status_code}",
                        "response": response.text[:500],
                    },
                }

        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return {
                "status": WhatsAppStatus.FAILED.value,
                "message_id": None,
                "provider": "meta",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": {"error": str(e)},
            }

    def is_configured(self) -> bool:
        return bool(self._access_token and self._phone_number_id)


def get_whatsapp_provider(
    provider_type: str = "mock",
    access_token: str = None,
    phone_number_id: str = None,
    default_recipient: str = None,
) -> WhatsAppProvider:
    """Factory: returns appropriate WhatsApp provider based on config."""
    if provider_type == "meta" and access_token and phone_number_id:
        return MetaWhatsAppProvider(
            access_token=access_token,
            phone_number_id=phone_number_id,
            default_recipient=default_recipient,
        )
    # Default to mock
    return MockWhatsAppProvider()
