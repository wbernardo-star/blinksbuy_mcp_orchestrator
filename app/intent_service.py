#TraceID intent_service.py

# app/intent_service.py
"""
Intent Service – Upgraded Version
Aligned with MCP Adapter v1.1 and MCP Orchestrator v1.1

Key Enhancements:
- trace_id propagation
- unified Loki logging
- microservice-safe output
"""

import os
import time
from typing import Optional
import requests

from .logging_loki import loki


INTENT_SERVICE_URL = os.getenv("INTENT_SERVICE_URL")


class IntentResult:
    def __init__(self, intent: str, confidence: float):
        self.intent = intent
        self.confidence = confidence


def classify_intent(
    text: str,
    user_id: str,
    channel: str,
    session_id: str,
    history=None,
    trace_id: Optional[str] = None
) -> IntentResult:

    start = time.perf_counter()

    fallback = IntentResult(intent="unknown", confidence=0.0)

    if not INTENT_SERVICE_URL:
        return fallback

    try:
        payload = {
            "text": text,
            "user_id": user_id,
            "channel": channel,
            "session_id": session_id
        }

        response = requests.post(INTENT_SERVICE_URL, json=payload, timeout=5)
        response.raise_for_status()
        data = response.json()

        intent = data.get("intent", "unknown")
        confidence = float(data.get("confidence", 0))

        latency_ms = round((time.perf_counter() - start) * 1000, 3)

        loki.log(
            "info",
            {
                "event_type": "intent_classified",
                "intent": intent,
                "confidence": confidence,
                "user": user_id,
                "channel": channel,
                "session_id": session_id,
                "latency_ms": latency_ms
            },
            service_type="intent_service",
            sync_mode="async",
            io="out",
            trace_id=trace_id
        )

        return IntentResult(intent=intent, confidence=confidence)

    except Exception as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 3)

        loki.log(
            "error",
            {
                "event_type": "intent_error",
                "user": user_id,
                "channel": channel,
                "session_id": session_id,
                "latency_ms": latency_ms,
                "error": str(e)
            },
            service_type="intent_service",
            sync_mode="async",
            io="none",
            trace_id=trace_id
        )

        return fallback
