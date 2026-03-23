# AEP + NemoClaw — Safety Enforcement for Sandboxed Agents

NemoClaw runs OpenClaw inside NVIDIA OpenShell sandboxes. The sandbox routes all inference through `inference.local`, which the OpenShell gateway forwards to a configured provider. By pointing the gateway at the AEP proxy, every LLM call gets safety enforcement.

## Architecture

```
+---------------------+     +-------------------+     +-------------+     +----------+
| NemoClaw Sandbox    | --> | OpenShell Gateway  | --> | AEP Proxy   | --> | LLM API  |
| (OpenClaw agent)    |     | (inference.local)  |     |             |     |          |
|                     |     |                    |     | - Safety    |     |          |
| No direct internet  |     | Routes inference   |     | - Cost      |     |          |
| No API keys in env  |     | to configured      |     | - Audit     |     |          |
|                     |     | provider           |     | - BLOCK     |     |          |
+---------------------+     +-------------------+     +-------------+     +----------+
```

The sandbox has no direct internet access and no API keys. The gateway injects credentials and routes inference. AEP sits between the gateway and the LLM, inspecting every request.

## Quick Start

```bash
./scripts/demo-nemoclaw.sh
```

This script:
1. Starts the AEP proxy in Docker
2. Creates an OpenShell provider pointing at the proxy
3. Configures inference routing through AEP
4. Creates a sandbox
5. Runs PASS + BLOCK test calls from inside the sandbox

## Manual Setup

### 1. Start AEP proxy

```bash
docker run -d --name aep-proxy -p 8899:8899 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  aep-proxy:local
```

### 2. Configure OpenShell provider

```bash
openshell provider create \
  --type openai \
  --name aep-proxy \
  --credential "OPENAI_API_KEY=$OPENAI_API_KEY" \
  --config "OPENAI_BASE_URL=http://host.docker.internal:8899/v1"
```

### 3. Route inference through AEP

```bash
openshell inference set --provider aep-proxy --model gpt-4o-mini
```

### 4. Create and test sandbox

```bash
openshell sandbox create --name test -- bash

# From inside sandbox:
curl -s https://inference.local/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}'
```

Watch the AEP dashboard at http://localhost:8899/aep/ — the call appears with cost and safety signals.

## Test Results (v0.5.2)

| Call | Input | Route | Result |
|------|-------|-------|--------|
| Normal | "What is 2+2?" | sandbox → gateway → AEP → OpenAI | **PASS** (HTTP 200) |
| Agent threat | socket.connect() + subprocess.run() | sandbox → gateway → AEP → **BLOCKED** | **BLOCK** (HTTP 400) |
| Normal after block | "List three benefits of open source" | sandbox → gateway → AEP → OpenAI | **PASS** (HTTP 200) |

The agent threat request never reached OpenAI. $0 cost. The proxy recovers normally after blocks.

## Cleanup

```bash
./scripts/demo-nemoclaw.sh --cleanup
```
