#TraceID flow_service.py

# app/flow_service.py
"""
Flow Service – Upgraded Version
Aligned with MCP Adapter v1.1 and MCP Orchestrator v1.1

Key Enhancements:
- Full trace_id propagation
- Unified logging via Loki
- Microservice-safe structure
- Backwards-compatible API
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
import time

from .logging_loki import loki
from .menu_service import get_menu


class FlowResult:
    def __init__(self, reply_text: str, route: str):
        self.reply_text = reply_text
        self.route = route


def run_flow(
    intent: str,
    text: str,
    user_id: str,
    channel: str,
    session_id: str,
    trace_id: Optional[str] = None
) -> FlowResult:
    """
    Main flow router for all domain-specific logic.

    Args:
        intent: classified intent
        text: user text from orchestrator
        user_id: id of user
        channel: origin channel
        session_id: orchestrator session
        trace_id: end-to-end tracing id

    Returns:
        FlowResult
    """

    start = time.perf_counter()

    try:
        # Example routing (extendable)
        if intent == "get_menu":
            menu = get_menu(user_id, channel, session_id, trace_id)
            reply = _format_menu(menu)
            route = "food_ordering.menu"

        else:
            reply = "I’m not sure how to help with that right now."
            route = "fallback.unknown"

        latency_ms = round((time.perf_counter() - start) * 1000, 3)

        loki.log(
            "info",
            {
                "event_type": "flow_output",
                "intent": intent,
                "route": route,
                "user": user_id,
                "channel": channel,
                "session_id": session_id,
                "latency_ms": latency_ms,
            },
            service_type="flow_service",
            sync_mode="async",
            io="out",
            trace_id=trace_id
        )

        return FlowResult(reply_text=reply, route=route)

    except Exception as e:
        latency_ms = round((time.perf_counter() - start) * 1000, 3)

        loki.log(
            "error",
            {
                "event_type": "flow_error",
                "intent": intent,
                "user": user_id,
                "channel": channel,
                "session_id": session_id,
                "latency_ms": latency_ms,
                "error": str(e)
            },
            service_type="flow_service",
            sync_mode="async",
            io="none",
            trace_id=trace_id
        )

        return FlowResult(
            reply_text="There was an issue processing your request.",
            route="system.error"
        )


def _format_menu(menu: Dict[str, Any]) -> str:
    """
    Helper to create readable menu text.
    """
    if not menu:
        return "Menu is temporarily unavailable."

    if "items" not in menu:
        return "Menu format error."

    lines = ["Here is the menu:"]
    for item in menu["items"]:
        name = item.get("name", "Unknown")
        price = item.get("price", "N/A")
        lines.append(f"- {name} – {price}")

    return "\n".join(lines)
