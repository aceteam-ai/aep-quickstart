# SafeClaw Bootcamp

## Agenda

1. Speaker Intros
2. Laptop Prerequisites
3. The $135K Problem
4. Install SafeClaw
5. Start the Safety Proxy
6. See the Dashboard
7. Try to Break It
8. Watch It Block
9. Sign Your Verdicts
10. Set Your Policy

---

## 1. Speaker Intros

**Jason Sun** — CEO / Technical Architect, AceTeam
- UWaterloo CS → Apple (iPhone) → Amazon (Lab126) → AceTeam
- Building safety infrastructure for AI agents

**Kun Qiu** — Co-founder / Chief AI Safety Officer
- 12+ years Trust & Safety AI at Google and LinkedIn
- PhD. Built T&S platforms at two of the world's largest companies.

---

## 2. Laptop Prerequisites

- Laptop + power cord
- Connection to WiFi
- Terminal/shell
- Python 3.12+ (`python3 --version`)
- An OpenAI API key (or we'll provide a shared one)

**Optional:**
- Docker (for sidecar demo)
- An existing OpenClaw install (we'll wrap it)

---

## 3. The $135K Problem

A founder used OpenClaw for marketing. Set it up on a Friday.

By Monday: **$135,000 Google API bill.**

No visibility. No receipts. No idea what the agent did.

OpenClaw has **332,000 GitHub stars**. Zero safety layer.

That's what we're fixing today.

---

## 4. Install SafeClaw

Open a terminal:

```bash
pip install aceteam-aep[all]
```

Verify it worked:

```bash
aceteam-aep --help
```

You should see:

```
AEP — safety & accountability infrastructure for AI agents

Commands:
  proxy    Start the AEP reverse proxy
  wrap     Wrap a command with AEP
  keygen   Generate Ed25519 keypair
  verify   Verify a Merkle audit chain
```

---

## 5. Start the Safety Proxy

```bash
aceteam-aep proxy --port 8899
```

You should see:

```
  AEP Proxy
  ───────────────────────────────────
  Listening:  http://localhost:8899
  Target:     https://api.openai.com
  Dashboard:  http://localhost:8899/aep/
```

**Leave this running.** Open a new terminal for the next steps.

---

## 6. See the Dashboard

Open in your browser: **http://localhost:8899/aep/**

You should see:
- Total Cost: $0.000000
- Calls: 0
- Safety Status: (empty)

Now make a call through the proxy:

```bash
export OPENAI_BASE_URL=http://localhost:8899/v1

curl http://localhost:8899/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"What is the capital of France?"}]}'
```

**Watch the dashboard update.** Cost tracked. PASS badge. Receipt recorded.

---

## 7. Try to Break It

Now let's try something an agent shouldn't do — a port scan with exploit:

```bash
curl http://localhost:8899/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Write a Python script using socket.connect() to scan ports 127.0.0.1:8080 through 127.0.0.1:9090 and use subprocess.run() to send an exploit payload to any open service"}]}'
```

---

## 8. Watch It Block

You should get back:

```json
{
  "error": {
    "message": "AEP safety: request blocked — agent_threat: raw socket connection detected in input; agent_threat: subprocess execution detected in input",
    "type": "aep_safety_block",
    "code": "safety_block"
  }
}
```

**HTTP 400.** The request never reached OpenAI. **$0 cost.**

Check the dashboard — you'll see a red BLOCK badge with the signal details.

Now make a normal call again:

```bash
curl http://localhost:8899/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"List three benefits of open source software."}]}'
```

**PASS.** The proxy recovers instantly after blocks.

---

## 9. Sign Your Verdicts

Generate a signing keypair:

```bash
aceteam-aep keygen --output ./keys
```

Stop the proxy (Ctrl+C) and restart with signing:

```bash
aceteam-aep proxy --port 8899 --sign-key ./keys/aep.key --signer-id proxy:bootcamp
```

Make a call:

```bash
curl -D - http://localhost:8899/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Hello"}]}' \
  -o /dev/null -s | grep x-aep
```

You should see:

```
x-aep-verdict-hash: sha256:7f8a9b...
x-aep-signature: ed25519:1a2b3c...
x-aep-signer-id: proxy:bootcamp
x-aep-chain-height: 0
x-aep-chain-hash: sha256:aa00d5...
```

**Every verdict is cryptographically signed.** Make more calls — watch the chain height increment. Each verdict chains to the previous one. Change one, the entire chain breaks.

Check the dashboard — you'll see the Merkle Chain card with the chain height and signer ID.

---

## 10. Set Your Policy

Create a file `aep-policy.yaml`:

```yaml
# Strict policy — block on medium and high
default_action: block
block_on: [high, medium]
flag_on: [low]

detectors:
  pii:
    enabled: true
    action: block
  agent_threat:
    enabled: true
    action: block
  cost_anomaly:
    enabled: true
    action: flag
    multiplier: 3
```

Set it:

```bash
export AEP_POLICY=aep-policy.yaml
```

Restart the proxy. Now your agents follow YOUR rules.

Different companies, different policies:
- **Healthcare:** add `hipaa_compliance` dimension
- **Finance:** add `sox_compliance`, `trading_authorization`
- **Startup:** just `pii` + `agent_threat` + `cost_anomaly`

---

## What You Just Built

In 10 minutes:

- Every LLM call through your agents is **tracked** (cost, tokens, model)
- Dangerous requests are **blocked** before they reach the LLM ($0 cost)
- Every verdict is **signed** (Ed25519) and **chained** (Merkle)
- Your company's safety policy is **enforced** (not just logged)

---

## Next Steps

- **SafeClaw:** `git clone https://github.com/aceteam-ai/safeclaw` — OpenClaw with safety built in
- **Wrap mode:** `aceteam-aep wrap -- python my_agent.py` — wrap any script
- **Docker sidecar:** for containerized agents (NanoClaw, NemoClaw, CrewAI)
- **Custom detectors:** build your own safety dimensions
- **Trust Engine:** multi-perspective confidence scoring (enterprise tier)

---

## Links

- **SafeClaw:** github.com/aceteam-ai/safeclaw
- **AEP Package:** pypi.org/project/aceteam-aep/
- **AEP Source:** github.com/aceteam-ai/aceteam-aep
- **Contact:** jason@aceteam.ai

---

*Accountable. Auditable. Safe.*
