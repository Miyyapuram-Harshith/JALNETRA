"""
JALNETRA Audit Service
======================
Records important events for accountability and replay.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import uuid

from app.schemas import AuditEntry


class AuditService:
    """Records system events for audit trail."""

    def __init__(self):
        self._entries: List[AuditEntry] = []

    def log(
        self,
        actor: str,
        action: str,
        previous_state: Optional[Dict[str, Any]] = None,
        new_state: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """Record an audit event."""
        entry = AuditEntry(
            id=f"audit-{uuid.uuid4().hex[:8]}",
            actor=actor,
            action=action,
            timestamp=datetime.now(timezone.utc),
            previous_state=previous_state,
            new_state=new_state,
            details=details or {},
        )
        self._entries.append(entry)

        # Keep last 1000 entries
        if len(self._entries) > 1000:
            self._entries = self._entries[-1000:]

        return entry

    def get_entries(self, limit: int = 100, action_filter: str = None) -> List[AuditEntry]:
        entries = self._entries
        if action_filter:
            entries = [e for e in entries if action_filter in e.action]
        return sorted(entries, key=lambda e: e.timestamp, reverse=True)[:limit]

    def reset(self):
        self._entries.clear()


# Singleton
audit_service = AuditService()
