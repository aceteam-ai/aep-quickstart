# AEP Quickstart — AI Agent Safety in 5 Minutes

Add cost tracking, safety detection, and enforcement to any AI agent. Zero code changes.

## What is AEP?

AEP (Agentic Execution Protocol) is a safety proxy that sits between your AI agent and the LLM API. It intercepts every call in both directions — blocking PII, toxic content, and cost anomalies before they reach your agent or the API.

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
source .env
uv run python main.py
```

You'll see:
- Call 1: normal question → **PASS**, cost tracked
- Call 2: asks for PII → model generates SSN/email → AEP detects → **BLOCK**
- Summary: total cost, safety status, signals

That's it. Your agent now has a safety layer.

### 4. Try the proxy (zero code changes to your agent)

```bash
source .env
uv run aceteam-aep proxy --port 8080
```

Open **http://localhost:8080/aep/** — this is your live safety dashboard.

In a new terminal:

```bash
source .env
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

## How It Works

```
Your Agent / Script
       |
       |  OPENAI_BASE_URL=http://localhost:8080/v1
       v
+------------------+
|   AEP Proxy      |  <-- intercepts both directions
|                   |
|  -> Check input   |  Block dangerous prompts BEFORE they reach OpenAI
|  -> Forward call  |
|  -> Check output  |  Block PII/toxic content BEFORE your agent sees it
|  -> Track cost    |  Per-call and cumulative cost tracking
|  -> Dashboard     |  Real-time web UI at /aep/
+------------------+
       |
       v
  OpenAI / Anthropic API
```

## Using with OpenClaw

OpenClaw hardcodes its API base URL, so `OPENAI_BASE_URL` won't work. Instead, configure a custom model provider in OpenClaw pointing at `http://localhost:8080/v1`.

See **[examples/07_openclaw.md](examples/07_openclaw.md)** for step-by-step instructions.

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

## Two Integration Paths

**Path 1: Proxy (recommended)** — zero code changes, works with any language/framework.
```bash
uv run aceteam-aep proxy --port 8080
export OPENAI_BASE_URL=http://localhost:8080/v1
# your existing code just works
```

**Path 2: Python SDK** — in-process wrapping for programmatic access.
```python
from aceteam_aep import wrap
client = wrap(openai.OpenAI())
print(client.aep.cost_usd)
print(client.aep.enforcement.action)
```

## Links

- **PyPI:** https://pypi.org/project/aceteam-aep/
- **Source:** https://github.com/aceteam-ai/aceteam-aep
- **Workshop Guide:** https://github.com/aceteam-ai/aceteam-aep/blob/main/docs/workshop-guide.md
- **Website:** https://aceteam.ai

## License

Apache 2.0
