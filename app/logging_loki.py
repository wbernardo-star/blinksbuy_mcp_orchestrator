# app/logging_loki.py
"""
Loki Logging Utility – Upgraded Version
Supports full trace_id propagation and consistent structured logging.
"""

import os
import json
import requests
from datetime import datetime, timezone


class LokiLogger:
    def __init__(self):
        self.url = os.getenv("LOKI_URL")
        self.tenant = os.getenv("LOKI_TENANT", "default")
        self.static_labels = os.getenv("LOKI_LABELS", "env=production")

    def log(
        self,
        level: str,
        payload: dict,
        service_type: str,
        sync_mode: str = "async",
        io: str = "none",
        trace_id: str = None
    ):
        if not self.url:
            return

        labels = {
            "service_type": service_type,
            "level": level,
            "io": io
        }

        if trace_id:
            labels["trace_id"] = trace_id

        if "session_id" in payload:
            labels["session_id"] = payload["session_id"]

        # Merge static labels (env=production,region=europe, etc.)
        for pair in self.static_labels.split(","):
            if "=" in pair:
                k, v = pair.split("=")
                labels[k.strip()] = v.strip()

        entry = {
            "streams": [
                {
                    "stream": labels,
                    "values": [
                        [
                            str(int(datetime.now(timezone.utc).timestamp() * 1e9)),
                            json.dumps(payload)
                        ]
                    ]
                }
            ]
        }

        try:
            headers = {
                "Content-Type": "application/json",
                "X-Scope-OrgID": self.tenant
            }
            requests.post(self.url, data=json.dumps(entry), headers=headers, timeout=2)
        except Exception:
            pass


loki = LokiLogger()
