# Using AEP with OpenClaw

OpenClaw is a Node.js agent that hardcodes its API base URL. It won't read `OPENAI_BASE_URL` from the environment. There are two ways to route it through the AEP safety proxy.

## Option A: Custom Model Config (Recommended)

OpenClaw supports custom model providers. Add a model entry that points at the AEP proxy.

### 1. Start the AEP proxy

```bash
cd /path/to/aep-quickstart
source .env
uv run aceteam-aep proxy --port 8080
```

### 2. Configure OpenClaw

Create or edit your OpenClaw settings to add a custom provider. The exact config location depends on your OpenClaw version, but typically you can configure models in the settings UI or via config files.

Add a provider with these settings:

```
Provider: OpenAI Compatible
API Base URL: http://localhost:8080/v1
API Key: (your OpenAI key)
Model ID: gpt-4o
```

This tells OpenClaw to route LLM calls through `localhost:8080` instead of directly to `api.openai.com`. The AEP proxy forwards to OpenAI transparently.

### 3. Run OpenClaw

Use OpenClaw normally. Every LLM call now flows through the AEP proxy.

Open **http://localhost:8080/aep/** to watch calls in real-time:
- Cost per call and cumulative spend
- Safety signals (PII, toxicity, cost anomalies)
- PASS / FLAG / BLOCK enforcement decisions

## Option B: For Python-Based Agents

If you're using a Python agent framework (LangChain, CrewAI, AutoGen, or raw OpenAI SDK), you don't need custom configs. Just set the env var:

```bash
export OPENAI_BASE_URL=http://localhost:8080/v1
python your_agent.py
```

The OpenAI Python SDK reads `OPENAI_BASE_URL` automatically.

## Option C: Any Language via curl

The proxy is just an HTTP endpoint. Any language that makes HTTP calls can use it:

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}]}'
```

Add governance context via headers:

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-AEP-Entity: org:acme" \
  -H "X-AEP-Classification: confidential" \
  -d '{"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "Hello"}]}'
```

## What You'll See on the Dashboard

Open http://localhost:8080/aep/ while your agent runs:

- **Cost counter** — real-time spend tracking
- **Safety badge** — green PASS, yellow FLAG, or red BLOCK
- **Signal list** — PII detected, toxic content, cost anomalies
- **Call timeline** — every LLM call with model name and duration

If the agent outputs PII (SSN, email, phone, credit card), the proxy blocks the response before your agent sees it. The dashboard shows a red BLOCK badge with the signal details.
