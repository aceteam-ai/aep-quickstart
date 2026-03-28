# AEP™ Quickstart — AI Agent Safety in 5 Minutes

Add cost tracking, safety detection, and enforcement to any AI agent. Zero code changes.

## What is AEP™?

AEP™ (Agentic Execution Protocol™) is a safety proxy that sits between your AI agent and the LLM API. It intercepts every call in both directions — blocking PII, toxic content, and cost anomalies before they reach your agent or the API.

Think of it like a firewall for AI agents.

## Quick Start

### 1. Clone and setup

```bash
git clone https://github.com/aceteam-ai/aep-quickstart.git
cd aep-quickstart
cp .env.example .env
# Edit .env — add your OPENAI_API_KEY
```

### 2. Install

```bash
uv sync
```

First run downloads ~300MB of safety models (cached after that).

### 3. Run it

```bash
uv run python main.py
```

The `.env` file is loaded automatically (via `python-dotenv`). No need to `source` it.

You'll see:
- Call 1: normal question → **PASS**, cost tracked
- Call 2: asks for PII → model generates SSN/email → AEP detects → **BLOCK**
- Summary: total cost, safety status, signals

That's it. Your agent now has a safety layer.

### 4. Try the proxy (zero code changes to your agent)

```bash
uv run aceteam-aep proxy --port 8080
```

Two dashboards:
- **http://localhost:8080/aep/** — Developer view (per-call signals, cost, timeline)
- **http://localhost:8080/aep/ciso** — Executive view (compliance frameworks, attestation, board-level summary)

In a new terminal:

```bash
export OPENAI_BASE_URL=http://localhost:8080/v1

# Basic call — should show PASS on dashboard
uv run python examples/01_basic.py

# Trigger PII detection — should show BLOCK
uv run python examples/02_pii_detection.py

# Cost tracking across multiple calls
uv run python examples/03_cost_tracking.py

# Python SDK (alternative to proxy)
uv run python examples/04_wrap_sdk.py

# Governance headers (any language)
bash examples/05_governance_headers.sh

# Custom safety detector
uv run python examples/06_custom_detector.py
```

Watch the dashboard update in real-time as each example runs.

## What the Proxy Sees

The proxy is a reverse proxy — it reads the **full request AND full response**. It can block in either direction.

| Data | Proxy Sees It? | Details |
|------|:--------------:|---------|
| User messages (input text) | **Yes** | Full message array from request |
| LLM response (output text) | **Yes** | Full response including all choices |
| Tool call requests | **Yes** | What functions the LLM asks to call |
| Tool call results | **Yes** | Included in the next request's messages |
| Token usage + cost | **Yes** | From response usage field |
| Agent actions between calls | **No** | File writes, code exec happen inside the agent |
| Application context | **No** | Unless sent via `X-AEP-*` headers (see example 05) |

**The proxy sees every word going to and from the LLM.** It cannot see what the agent does *between* LLM calls.

## How It Works

```
Your Agent / Script
       |
       |  OPENAI_BASE_URL=http://localhost:8080/v1
       v
+------------------+
|   AEP Proxy      |  <-- reads FULL request + response
|                   |
|  -> Check input   |  Block dangerous prompts BEFORE they reach OpenAI
|  -> Forward call  |  (or block — call never leaves your machine)
|  -> Check output  |  Block PII/toxic content BEFORE your agent sees it
|  -> Track cost    |  Per-call and cumulative cost tracking
|  -> Dashboard     |  Developer (/aep/) + Executive (/aep/ciso)
+------------------+
       |
       v
  OpenAI / Anthropic API
```

## Using with OpenClaw

OpenClaw hardcodes its API base URL, so `OPENAI_BASE_URL` won't work. Instead, configure a custom model provider in OpenClaw pointing at `http://localhost:8080/v1`.

See **[examples/07_openclaw.md](examples/07_openclaw.md)** for step-by-step instructions.

## Using with NemoClaw / OpenShell

AEP works as a sidecar to NemoClaw sandboxes. The OpenShell gateway routes inference through the AEP proxy — the sandbox has no direct internet access and no API keys.

```bash
# One-command demo (requires openshell CLI)
./scripts/demo-nemoclaw.sh
```

Tested and verified: agent threat requests (port scanning, subprocess execution) are **blocked at the proxy before reaching the LLM**. Normal calls pass through with cost tracking and safety receipts.

See **[examples/09_nemoclaw.md](examples/09_nemoclaw.md)** for architecture details and manual setup.

## Sidecar Pattern (Docker)

For any containerized agent, add AEP as a sidecar:

```bash
docker compose -f docker-compose.sidecar.yml up
```

One env var (`OPENAI_BASE_URL=http://aep-proxy:8899/v1`), zero code changes. Works with NanoClaw, CrewAI, DeerFlow, or any custom agent image.

See **[examples/08_sidecar.md](examples/08_sidecar.md)** for the full pattern including K8s pod spec.

## Examples Overview

| File | What It Shows |
|------|--------------|
| `01_basic.py` | Simple call through proxy, dashboard shows PASS |
| `02_pii_detection.py` | PII in output triggers BLOCK |
| `03_cost_tracking.py` | Multiple calls, cost accumulation, anomaly detection |
| `04_wrap_sdk.py` | Python SDK alternative (no proxy needed) |
| `05_governance_headers.sh` | Governance via HTTP headers (any language) |
| `06_custom_detector.py` | Build your own safety detector |
| `07_openclaw.md` | OpenClaw-specific setup guide |
| `08_sidecar.md` | Docker sidecar pattern for any containerized agent |
| `09_nemoclaw.md` | NemoClaw/OpenShell integration with AEP proxy |

## Two Layers: Proxy + SDK

Think **WireGuard + Tailscale**. WireGuard is the wire protocol. Tailscale adds identity on top.

**Layer 1 — Proxy (free, zero code changes)**
- Sees all LLM traffic (input, output, tool calls, cost)
- Runs safety detectors, enforces PASS/FLAG/BLOCK
- Works with any language, any framework
```bash
uv run aceteam-aep proxy --port 8080
export OPENAI_BASE_URL=http://localhost:8080/v1
# your existing code just works
```

**Layer 2 — SDK + Headers (application context)**
- Adds identity, governance, provenance
- For things the proxy can't see (who is calling, data classification)
- Via `X-AEP-*` HTTP headers (any language) or Python `wrap()`
```python
from aceteam_aep import wrap
client = wrap(openai.OpenAI())
print(client.aep.cost_usd)
print(client.aep.enforcement.action)
```

Layer 1 gets you in the door. Layer 2 makes you enterprise-ready.

## Links

- **PyPI:** https://pypi.org/project/aceteam-aep/
- **Source:** https://github.com/aceteam-ai/aceteam-aep
- **Workshop Guide:** https://github.com/aceteam-ai/aceteam-aep/blob/main/docs/workshop-guide.md
- **Website:** https://aceteam.ai

## Trademarks

"Agentic Execution Protocol," "AEP," and "AceTeam" are trademarks of AceTeam. The software is licensed under Apache 2.0. The trademark is not included in the license grant — you may not use these names to endorse or promote derivative works without written permission.

## License

Apache 2.0
