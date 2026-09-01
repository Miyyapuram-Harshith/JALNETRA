"""
JALNETRA WebSocket Manager
===========================
Real-time event broadcasting over WebSocket channels.
Supports multiple channels and polling fallback.
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set, Any
from datetime import datetime, timezone
import json
import logging
import asyncio

logger = logging.getLogger("jalnetra.websocket")


class WebSocketManager:
    """
    Manages WebSocket connections and broadcasts events.

    Channels:
        risk, sensors, alerts, incidents, routes, simulation, system

    Events:
        RISK_UPDATED, RISK_ESCALATED, RISK_DEESCALATED,
        SENSOR_UPDATED, SENSOR_OFFLINE, SENSOR_ANOMALY,
        ROAD_THREATENED, ROUTE_CHANGED, SHELTER_CHANGED,
        ALERT_ISSUED, INCIDENT_CREATED,
        NETWORK_DEGRADED, NETWORK_RESTORED,
        SIMULATION_UPDATED
    """

    def __init__(self):
        self._connections: Dict[str, List[WebSocket]] = {}
        self._last_events: Dict[str, Dict] = {}  # For polling fallback

    async def connect(self, websocket: WebSocket, channel: str):
        """Accept a WebSocket connection on a channel."""
        await websocket.accept()
        if channel not in self._connections:
            self._connections[channel] = []
        self._connections[channel].append(websocket)
        logger.info(f"WebSocket connected: channel={channel}, total={len(self._connections[channel])}")

    def disconnect(self, websocket: WebSocket, channel: str):
        """Remove a WebSocket connection."""
        if channel in self._connections:
            self._connections[channel] = [
                ws for ws in self._connections[channel] if ws != websocket
            ]
            logger.info(f"WebSocket disconnected: channel={channel}")

    async def broadcast(self, channel: str, event_type: str, data: Any):
        """Broadcast an event to all connections on a channel."""
        message = {
            "event": event_type,
            "channel": channel,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Store for polling fallback
        self._last_events[channel] = message

        # Broadcast to all connected clients
        if channel in self._connections:
            dead_connections = []
            for ws in self._connections[channel]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead_connections.append(ws)

            # Clean up dead connections
            for ws in dead_connections:
                self._connections[channel] = [
                    c for c in self._connections[channel] if c != ws
                ]

    async def broadcast_all(self, event_type: str, data: Any):
        """Broadcast to ALL channels."""
        channels = list(self._connections.keys())
        for channel in channels:
            await self.broadcast(channel, event_type, data)

    def get_last_event(self, channel: str) -> Dict:
        """Get last event for polling fallback."""
        return self._last_events.get(channel, {
            "event": "NO_DATA",
            "channel": channel,
            "data": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_connection_count(self) -> Dict[str, int]:
        """Get connection count per channel."""
        return {ch: len(conns) for ch, conns in self._connections.items()}

    def is_healthy(self) -> bool:
        return True  # WebSocket manager is always healthy (stateless)


# Singleton
ws_manager = WebSocketManager()
