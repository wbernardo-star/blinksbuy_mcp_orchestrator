#TraceID menu_service.py



# app/menu_service.py
"""
Menu Service – Upgraded Version
Aligned with MCP Adapter v1.1 and MCP Orchestrator v1.1

Key Enhancements:
- Full trace_id propagation (end-to-end observability)
- Structured Loki logging
- Robust error handling with latency measurement
- Same functional contract (backward compatible)
- Microservice-safe return types
"""

import os
import time
from typing import Dict, Any, Optional

import requests

from .logging_loki import loki


MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL")


def get_menu(
    user_id: str,
    channel: str,
    session_id: str,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch menu data from the external Menu Microservice.

    Args:
        user_id: ID of the user making the request
        channel: Channel (web, voice, WhatsApp, etc.)
        session_id: Orchestrator session id
        trace_id: End-to-end trace identifier for observability (optional)

    Returns:
        A dict containing menu data.
        Returns {} on failure.
    """

    start_time = time.perf_counter()

    if not MENU_SERVICE_URL:
        loki.log(
            "error",
            {
                "event_type": "service_error",
                "user": user_id,
                "channel": channel,
                "session_id": session_id,
                "error": "MENU_SERVICE_URL not configured"
            },
            service_type="menu_service",
            sync_mode="async",
            io="none",
            trace_id=trace_id
        )
        return {}

    try:
        response = requests.get(MENU_SERVICE_URL, timeout=5)
        response.raise_for_status()

        latency_ms = round((time.perf_counter() - start_time) * 1000, 3)

        loki.log(
            "info",
            {
                "event_type": "service_called",
                "service": "menu_service",
                "user": user_id,
                "channel": channel,
                "session_id": session_id,
                "latency_ms": latency_ms,
                "status": "success",
                "http_status": response.status_code
            },
            service_type="menu_service",
            sync_mode="async",
            io="out",
            trace_id=trace_id
        )

        # Convert JSON to dict (safe)
        return response.json() if response.content else {}

    except Exception as e:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 3)

        loki.log(
            "error",
            {
                "event_type": "service_error",
                "service": "menu_service",
                "user": user_id,
                "channel": channel,
                "session_id": session_id,
                "latency_ms": latency_ms,
                "error": str(e)
            },
            service_type="menu_service",
            sync_mode="async",
            io="none",
            trace_id=trace_id
        )

        return {}
