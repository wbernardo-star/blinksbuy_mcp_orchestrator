# MCP Orchestrator  
Model Context Protocol – Intent Routing and Flow Execution  
Version 1.1

## Overview

The MCP Orchestrator is the central coordination layer of the Model Context Protocol (MCP) platform. It receives normalized requests from the MCP Adapter and performs:

1. Intent classification  
2. Domain flow routing  
3. Lightweight session management  
4. Structured observability (trace_id, Loki logging, Grafana dashboards)  
5. Producing a compact orchestration response consumed by the MCP Adapter

The orchestrator does not generate canonical envelopes.  
It delegates this responsibility to the MCP Adapter, ensuring clean separation of concerns.

## Architectural Role

Client → Channel → MCP Adapter (Canonical v1.1) → MCP Orchestrator  
           → Intent Service → Flow Service → MCP Adapter → Client

## Key Features

- Full trace_id propagation from adapter into orchestrator logs and back to adapter  
- Structured logging to Loki with consistent labeling  
- Lightweight session state (turn count and timestamps)  
- Delegates domain logic to Flow Services  
- Delegates intent classification to Intent Service  
- Simple, stable, contract-based JSON output  
- Fully aligned with MCP Adapter Canonical JSON v1.1  

## Environment Variables

| Variable | Description |
|----------|-------------|
| LOKI_URL | Loki ingestion endpoint |
| LOKI_TENANT | Tenant for multi-tenant logging |
| LOKI_LABELS | Additional labels applied to logs |
| OPENAI_API_KEY or INTENT_MODEL_KEY | Intent classifier configuration |
| Flow-specific variables | Used by flow microservices |

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

## Full Canonical Response v1.1 (Success)

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

## Full Canonical Response v1.1 (Error)

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

Includes:
- trace_id
- session_id
- user_id
- channel
- event_type
- latency_ms
- intent and confidence
- route

## Session Management

Minimal in-memory session data:
- turn count
- last active timestamp
- last route

## Grafana Dashboard

Provided under:
grafana/mcp_orchestrator_loki_dashboard.json

## Project Structure

app/
  main.py
  flow_service.py
  intent_service.py
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

Configure environment variables in Railway.

