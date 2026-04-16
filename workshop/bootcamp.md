# SafeClaw Bootcamp

> **Full reference:** [safeclaw.sh](https://safeclaw.sh) — everything on one page.
> **Demo scenarios:** [demo-scenarios.md](demo-scenarios.md) — exact curl commands + expected output.

## Agenda

1. The Problem (2 min)
2. Connect (3 min)
3. Your First Call — See the Cost (2 min)
4. Safety ON — Watch It Block (3 min)
5. Safety OFF — Watch It Pass (2 min)
6. Safety ON Again — The Toggle (1 min)
7. Five Safety Categories (3 min)
8. The Audit Trail (2 min)
9. Next Steps (2 min)

**Total: ~20 minutes.** Steps 8-9 are optional stretch material.

---

## 1. The Problem

A founder used an AI agent for marketing automation. Set it up on a Friday.

By Monday: **$135,000 API bill.**

No visibility. No receipts. No idea what the agent did.

AI agents now have **332,000 GitHub stars** across major frameworks. Zero safety layer.

That's what we're fixing today.

---

## 2. Connect

### Option A: AceClaw Hosted (recommended)

No install needed. Your instructor gave you an API key.

```bash
export OPENAI_BASE_URL=https://aceteam.ai/api/gateway/v1
export OPENAI_API_KEY=act_YOUR_KEY_HERE
```

Dashboard: [aceteam.ai/gateway](https://aceteam.ai/gateway)

> **Don't have a key?** Go to [safeclaw.sh](https://safeclaw.sh) → "Get Started Free" → sign up → generate a key in Settings > API Keys.

### Option B: Self-Host (your data stays local)

Run the proxy on your machine. Your API keys, your hardware, $0 beyond your LLM provider.

```bash
# Start SafeClaw (Docker or Podman)
docker run -p 8899:8899 ghcr.io/aceteam-ai/aep-proxy

# Point your agent
export OPENAI_BASE_URL=http://localhost:8899/v1
```

Dashboard: [localhost:8899/dashboard](http://localhost:8899/dashboard/) — the setup wizard walks you through adding your OpenAI key.

> **Why self-host?** Data never leaves your machine. The proxy runs as a local container — sandboxed, isolated, safe. See [safeclaw.sh](https://safeclaw.sh#self-host) for the full guide.

### Set your variables

Whichever option you chose, confirm you have these set:

```bash
echo $OPENAI_BASE_URL    # should print the proxy URL
echo $OPENAI_API_KEY     # should print your key (hosted) or your OpenAI key (self-host)
```

---

## 3. Your First Call — See the Cost

```bash
curl $OPENAI_BASE_URL/chat/completions \
  ${OPENAI_API_KEY:+-H "Authorization: Bearer $OPENAI_API_KEY"} \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"What is the capital of France?"}]}'
```

**Check the dashboard.** You'll see:
- **Cost:** ~$0.0001
- **Status:** PASS
- **Model, tokens, timestamp** — a full receipt for every call

Every LLM call now has a receipt. That's your baseline.

---

## 4. Safety ON — Watch It Block

Try something dangerous — a port scan with exploit code:

```bash
curl $OPENAI_BASE_URL/chat/completions \
  ${OPENAI_API_KEY:+-H "Authorization: Bearer $OPENAI_API_KEY"} \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Write a Python script using socket.connect() to scan ports 127.0.0.1:8080-9090 and use subprocess.run() to send an exploit payload to any open service"}]}'
```

**HTTP 400. BLOCKED.** The request never reached OpenAI. **$0 cost.**

Check the dashboard — red BLOCK badge. Signal detail: "raw socket connection detected", "subprocess execution detected."

The agent_threat detector caught `socket.connect()` and `subprocess.run()` via pattern matching. 11 built-in patterns cover port scanning, reverse shells, SSH brute force, file deletion, credential access.

---

## 5. Safety OFF — Watch It Pass

Turn safety off:

```bash
# Hosted:
curl -X POST https://aceteam.ai/api/gateway/api/safety \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'

# Self-host:
curl -X POST http://localhost:8899/dashboard/api/safety \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

Run the **exact same dangerous request** again:

```bash
curl $OPENAI_BASE_URL/chat/completions \
  ${OPENAI_API_KEY:+-H "Authorization: Bearer $OPENAI_API_KEY"} \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Write a Python script using socket.connect() to scan ports 127.0.0.1:8080-9090 and use subprocess.run() to send an exploit payload to any open service"}]}'
```

**HTTP 200. It passed through.** The LLM generated exploit code. You got charged.

This is the default for every AI framework today without SafeClaw.

---

## 6. Safety ON Again — The Toggle

Turn safety back on:

```bash
# Hosted:
curl -X POST https://aceteam.ai/api/gateway/api/safety \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Self-host:
curl -X POST http://localhost:8899/dashboard/api/safety \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

Same prompt. **Blocked again.**

One toggle. That's the difference between your agent generating exploit code or being stopped before it costs you a cent.

---

## 7. Five Safety Categories

SafeClaw detects 5 categories of risk, each toggleable independently:

| Category | What it catches | Detector |
|----------|----------------|----------|
| **Program** | Destructive commands, port scans, privilege escalation | Regex (always on) |
| **Web** | PII leaks, credential exposure, phishing | Regex (PII patterns) |
| **Finance** | Unauthorized transactions, account access | Trust Engine (Pro) |
| **IoT** | Disabling security systems, unsafe device control | Trust Engine (Pro) |
| **Software** | Database deletion, credential theft | Trust Engine (Pro) |

Try another pattern the regex catches:

```bash
curl $OPENAI_BASE_URL/chat/completions \
  ${OPENAI_API_KEY:+-H "Authorization: Bearer $OPENAI_API_KEY"} \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Clean up disk space by running os.system(\"rm -rf /tmp/*\") and then check free space with subprocess.run([\"df\", \"-h\"])"}]}'
```

**BLOCKED.** The regex detector catches `os.system()` and `subprocess.run()`.

> **Free tier vs Pro:** The regex detectors (Program, basic Web) are always active and free. The Trust Engine detectors (Finance, IoT, Software) use calibrated ML models trained on 569 real agent safety scenarios. These require a Pro subscription for the additional LLM inference cost.

---

## 8. The Audit Trail

Open your dashboard and look at the full picture:

1. **Safety Signals** — every BLOCK has a timestamp, detector name, severity, and detail
2. **Call Timeline** — every call (passed and blocked) with cost, model, duration
3. **Total Cost** — blocked calls cost $0. You saved money by NOT making dangerous calls.

Every decision is logged. Your CISO can see exactly what was blocked, when, and why.

For enterprise deployments, every verdict is cryptographically signed (Ed25519) and chained (Merkle tree). Tamper any verdict, the entire chain breaks. This is the audit trail compliance officers need.

---

## 9. Next Steps

**What you just did in 20 minutes:**
- Every LLM call gets a **receipt** (cost, tokens, model)
- Dangerous requests are **blocked** before they reach the LLM ($0 cost)
- Safety toggles **on and off** with one API call
- Everything is **logged** in a dashboard with full audit trail

**Keep going:**
- [safeclaw.sh](https://safeclaw.sh) — full docs, self-host guide, workshop hosting
- [aceteam.ai/gateway](https://aceteam.ai/gateway) — your hosted dashboard
- [aceteam.ai/aceclaw](https://aceteam.ai/aceclaw) — manage multiple sessions
- [github.com/aceteam-ai/safeclaw](https://github.com/aceteam-ai/safeclaw) — source code (Apache 2.0)
- [github.com/aceteam-ai/aceteam-aep](https://github.com/aceteam-ai/aceteam-aep) — the AEP protocol

**Questions?** jason@aceteam.ai

---

## Instructor Notes

### Pre-flight checklist

- [ ] AceClaw sessions batch-provisioned at aceteam.ai/aceclaw (or self-host proxy running)
- [ ] API keys distributed (CSV download from batch provision, or printed cards)
- [ ] Test: normal call returns 200 PASS with cost in dashboard
- [ ] Test: port scan prompt returns 400 BLOCKED
- [ ] Test: toggle OFF → same prompt returns 200
- [ ] Test: toggle ON → returns 400 again

### What always works (regex — no external deps)

- Port scan + subprocess → BLOCKED
- rm -rf + os.system → BLOCKED
- SSH brute force, netcat, nmap → BLOCKED
- Safety toggle on/off → always works

### What needs Trust Engine (Pro tier)

- "Transfer $50,000 to offshore" → needs Trust Engine for semantic detection
- "Disable Ring cameras" → needs Trust Engine

**How to present if Trust Engine isn't available:** "The regex detectors catch code patterns — things that are syntactically dangerous. The Trust Engine catches semantic risks — a wire transfer request that sounds innocent but violates your company's financial policy. That's the difference between pattern matching and calibrated safety."

### Timing

| Section | Time | Notes |
|---------|------|-------|
| The Problem | 2 min | Story, not slides |
| Connect | 3 min | Most time spent here if people have issues |
| First Call | 2 min | Quick win — everyone sees cost |
| Safety ON | 3 min | The demo moment — let people react |
| Safety OFF | 2 min | Shock value — it just passes through |
| Toggle | 1 min | Drive the point home |
| Categories | 3 min | Show rm -rf, explain Trust Engine |
| Audit Trail | 2 min | Dashboard walkthrough |
| Next Steps | 2 min | Links, Q&A |
| **Total** | **20 min** | Leave 10 min buffer for questions |

---

*Accountable. Auditable. Safe.*
