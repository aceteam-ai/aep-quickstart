# AEP Sidecar Pattern — Zero Code Changes for Any Agent

The sidecar proxy sits at the **network level**. It doesn't matter how the agent is configured internally — if LLM traffic routes through the proxy, every call gets cost tracking, safety detection, and audit trails.

## Quick Start

```bash
cp .env.example .env  # add OPENAI_API_KEY
docker compose -f docker-compose.sidecar.yml up
```

Dashboard: http://localhost:8899/aep/

## How It Works

```
+------------------+       +-------------+       +----------+
| Agent Container  | ----> | AEP Sidecar | ----> | LLM API  |
| (any framework)  |       | Proxy       |       |          |
|                  |       |             |       |          |
| OPENAI_BASE_URL= |       | - Safety    |       |          |
|  http://aep:8899 |       | - Cost      |       |          |
|                  |       | - Audit     |       |          |
+------------------+       +-------------+       +----------+
```

One environment variable. Zero code changes. The agent doesn't know AEP exists.

## Works With

| Framework | How to route through AEP |
|-----------|-------------------------|
| **Python (OpenAI SDK)** | `OPENAI_BASE_URL=http://aep-proxy:8899/v1` — SDK reads it automatically |
| **Python (Anthropic SDK)** | `ANTHROPIC_BASE_URL=http://aep-proxy:8899/v1` |
| **NanoClaw** | `OPENAI_BASE_URL=http://aep-proxy:8899/v1` |
| **CrewAI** | `OPENAI_BASE_URL=http://aep-proxy:8899/v1` |
| **DeerFlow** | `OPENAI_BASE_URL=http://aep-proxy:8899/v1` |
| **OpenClaw** | Custom provider config pointing at `http://aep-proxy:8899/v1` (see `examples/07_openclaw.md`) |
| **NemoClaw** | Configure OpenShell gateway's inference endpoint to point at AEP proxy |
| **Any HTTP client** | Send requests to `http://aep-proxy:8899/v1/chat/completions` |

## Running the Python Example

```bash
docker compose -f docker-compose.sidecar.yml --profile python up
```

This starts the AEP proxy and a Python container that makes an LLM call through it. Watch the dashboard update in real-time.

## Production Deployment (Kubernetes)

In K8s, add the AEP proxy as a sidecar container in your agent pod:

```yaml
spec:
  containers:
    - name: agent
      image: your-agent:latest
      env:
        - name: OPENAI_BASE_URL
          value: http://localhost:8899/v1
    - name: aep-proxy
      image: ghcr.io/aceteam-ai/aep-proxy:latest
      ports:
        - containerPort: 8899
      env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: llm-keys
              key: openai
```

Every agent pod gets an AEP sidecar. Every LLM call gets a receipt.
