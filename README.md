# MCP Orchestrator  
Model Context Protocol – Intent Routing and Flow Execution  
Version 1.1

## Overview

The MCP Orchestrator is the central coordination layer of the Model Context Protocol (MCP) platform. It receives normalized requests from the MCP Adapter and performs:

1. Intent classification via the Intent Service  
2. Domain flow routing via Flow Services  
3. Lightweight session management  
4. Structured observability with trace_id, Loki, and Grafana  
5. Returning a thin orchestration response that the MCP Adapter wraps into Canonical JSON v1.1

The orchestrator is intentionally thin. It delegates domain behavior to flow services and avoids responsibility for canonical envelopes, multimodal handling, or error envelopes. These concerns belong to the MCP Adapter.

## Role in the MCP Architecture

Client → Channel → MCP Adapter → MCP Orchestrator  
        → Intent Service → Flow Services → MCP Adapter → Client

Responsibilities:

- MCP Adapter: Canonical v1.1 envelopes, multimodal normalization, trace_id management  
- MCP Orchestrator: Intent routing, flow delegation, session turn tracking, logging  
- Intent Service: LLM-based classification  
- Flow Services: Domain-specific business logic

The orchestrator returns thin JSON, not canonical format.

## Environment Variables

| Variable | Description |
|----------|-------------|
| LOKI_URL | Loki ingestion endpoint |
| LOKI_TENANT | Loki tenant ID |
| LOKI_LABELS | Static Loki labels |
| INTENT_SERVICE_URL | URL for intent classifier |
| MENU_SERVICE_URL | URL for menu domain service |
| Additional service URLs | Optional based on domain |

## API Endpoints

### GET /health

Response:
{
  "status": "ok",
  "service": "mcp_orchestrator_thin"
}

### POST /orchestrate

Expected Request:
{
  "text": "Can you read me the menu?",
  "user_id": "user-123",
  "channel": "web",
  "session_id": "user-123:web",
  "trace_id": "trace-123abc"
}

## Orchestrator Output Contract

Example Orchestrator Response:
{
  "decision": "reply",
  "reply_text": "Here is the menu.",
  "session_id": "user-123:web",
  "route": "food_ordering.menu",
  "intent": "get_menu",
  "intent_confidence": 0.98,
  "trace_id": "trace-123abc"
}

## Canonical Response v1.1 (Success)

{
  "version": "1.1",
  "timestamp": "2025-11-21T21:28:56.146Z",
  "context": {
    "channel": "web",
    "device": "browser",
    "locale": "en-US",
    "tenant": "blinksbuy",
    "client_app": "elevenlabs"
  },
  "session": {
    "session_id": "user-123:web",
    "conversation_id": "conv-001",
    "user_id": "user-123",
    "turn": 4,
    "route": "food_ordering.menu"
  },
  "response": {
    "status": "success",
    "code": 200,
    "type": "text",
    "text": "Here is the menu:\n1. Garlic Chicken – 500\n2. Sizzling Pata – 650\n3. Sisig – 400",
    "metadata": {
      "source": "mcp_orchestrator",
      "duration_ms": 16250.315
    }
  },
  "error": null,
  "observability": {
    "trace_id": "trace-123abc",
    "span_id": "span-outbound-1",
    "message_id": "msg-0003"
  }
}

## Canonical Response v1.1 (Error)

{
  "version": "1.1",
  "timestamp": "2025-11-21T21:28:56.146Z",
  "context": {
    "channel": "web",
    "device": "browser",
    "locale": "en-US",
    "tenant": "blinksbuy",
    "client_app": "elevenlabs"
  },
  "session": {
    "session_id": "user-123:web",
    "conversation_id": "conv-001",
    "user_id": "user-123",
    "turn": 4,
    "route": null
  },
  "response": {
    "status": "error",
    "code": 502,
    "type": "text",
    "text": null,
    "metadata": {
      "source": "mcp_adapter",
      "duration_ms": 112.529
    }
  },
  "error": {
    "type": "MCP_ORCHESTRATOR_ERROR",
    "code": 502,
    "message": "MCP orchestrator error: 500 Internal error in orchestrator",
    "retryable": false,
    "details": {
      "mcp_url": "https://your-mcp-service.railway.app/orchestrate"
    }
  },
  "observability": {
    "trace_id": "trace-123abc",
    "span_id": "span-error-1",
    "message_id": "msg-err-001"
  }
}

## Logging and Observability

Every service (orchestrator, intent, flow, menu) logs with:
- trace_id  
- session_id  
- user  
- channel  
- event_type  
- latency_ms  
- intent / confidence  
- route  

These logs feed a Grafana dashboard for:
- trace-based debugging  
- flow execution visibility  
- latency monitoring  
- error analytics  
- intent distribution  
- route frequency  

## Project Structure

app/
  main.py  
  flow_service.py  
  intent_service.py  
  menu_service.py  
  logging_loki.py  

grafana/
  mcp_orchestrator_loki_dashboard.json  

Procfile  
requirements.txt  
README.md  

## Local Development

pip install -r requirements.txt  
uvicorn app.main:app --host 0.0.0.0 --port 8000

## Railway Deployment

Procfile:
web: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

Configure Railway variables:
- LOKI_URL  
- LOKI_TENANT  
- LOKI_LABELS  
- INTENT_SERVICE_URL  
- MENU_SERVICE_URL  

## Summary

This orchestrator implementation is fully aligned with:
- MCP Adapter Canonical JSON v1.1  
- end-to-end traceability  
- structured observability  
- modular intent and flow service architecture  
- Railway-ready deployment

