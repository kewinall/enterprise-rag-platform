from __future__ import annotations

import json
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4

from app.core.config import get_settings

SCHEMA_VERSION = "1.0"


class OperationalFeedbackWriter:
    def __init__(
        self,
        path: Path,
        *,
        consumer_name: str,
        consumer_version: str,
        environment: str,
        evidence_kind: str,
    ) -> None:
        self.path = path
        self.consumer = {
            "name": consumer_name,
            "version": consumer_version,
            "environment": environment,
            "evidence_kind": evidence_kind,
        }
        self._lock = Lock()

    @staticmethod
    def new_query_id() -> str:
        return f"q-{uuid4()}"

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat()

    def _base_event(self, event_type: str) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "event_id": f"evt-{uuid4()}",
            "occurred_at": self._now(),
            "event_type": event_type,
            "consumer": dict(self.consumer),
        }

    def _append(self, event: dict[str, Any]) -> str:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        rendered = json.dumps(event, ensure_ascii=False, separators=(",", ":"))
        with self._lock, self.path.open("a", encoding="utf-8") as handle:
            handle.write(rendered + "\n")
        return str(event["event_id"])

    @staticmethod
    def _document_ids(results: list[dict[str, Any]]) -> list[str]:
        document_ids: list[str] = []
        seen: set[str] = set()
        for result in results:
            document_id = result.get("document_id")
            if (
                isinstance(document_id, str)
                and document_id
                and document_id != "unknown"
                and document_id not in seen
            ):
                seen.add(document_id)
                document_ids.append(document_id)
        return document_ids

    def emit_search(
        self,
        *,
        query_id: str,
        results: list[dict[str, Any]],
        explicit_feedback: str | None = None,
    ) -> str:
        event = self._base_event("search")
        event.update(
            {
                "query_id": query_id,
                "result_count": len(results),
                "outcome": "results" if results else "no_results",
                "top_document_ids": self._document_ids(results),
            }
        )
        if explicit_feedback is not None:
            event["explicit_feedback"] = explicit_feedback
        return self._append(event)

    def emit_citation_click(self, *, query_id: str, document_id: str, rank: int) -> str:
        event = self._base_event("citation_click")
        event.update(
            {
                "query_id": query_id,
                "document_id": document_id,
                "rank": rank,
            }
        )
        return self._append(event)

    def emit_troubleshooting_reuse(self, *, document_id: str, outcome: str) -> str:
        event = self._base_event("troubleshooting_reuse")
        event.update({"document_id": document_id, "outcome": outcome})
        return self._append(event)

    def emit_lifecycle_feedback(
        self,
        *,
        document_id: str,
        reason: str,
        severity: str,
    ) -> str:
        event = self._base_event("lifecycle_feedback")
        event.update(
            {
                "document_id": document_id,
                "reason": reason,
                "severity": severity,
            }
        )
        return self._append(event)


@lru_cache
def get_live_feedback_writer() -> OperationalFeedbackWriter | None:
    settings = get_settings()
    if not settings.operational_feedback_enabled:
        return None
    return OperationalFeedbackWriter(
        Path(settings.operational_feedback_path),
        consumer_name=settings.operational_feedback_consumer_name,
        consumer_version=settings.app_version,
        environment=settings.app_env,
        evidence_kind="live_consumer",
    )
