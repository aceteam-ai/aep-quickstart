"""Pillar 4: Governance — classification, consent, budget via proxy headers.

Runs 3 scenarios through the AEP proxy with different governance contexts:
  1. Public data, full consent
  2. Confidential data, no training consent
  3. Restricted data, tight budget, minimal consent

The proxy strips X-AEP-* headers before forwarding to the LLM and
returns enforcement decisions in response headers.

Requires proxy running:
    uv run aceteam-aep proxy --port 8080
"""

from dotenv import load_dotenv

load_dotenv()

import os
import sys

import httpx

PROXY = os.environ.get("OPENAI_BASE_URL", "http://localhost:8080/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Check proxy is running
try:
    httpx.get(PROXY.replace("/v1", "/aep/"), timeout=2)
except (httpx.ConnectError, httpx.ReadTimeout):
    print(f"Proxy not running at {PROXY}")
    print("Start it:  uv run aceteam-aep proxy --port 8080")
    sys.exit(1)

print("=" * 60)
print("PILLAR 4: GOVERNANCE")
print("=" * 60)

SCENARIOS = [
    {
        "label": "Public data — full consent",
        "content": "What are the key trends in AI infrastructure?",
        "headers": {
            "X-AEP-Entity": "org:acme",
            "X-AEP-Classification": "public",
            "X-AEP-Consent": "training=yes,sharing=yes",
            "X-AEP-Budget": "5.00",
        },
    },
    {
        "label": "Confidential — no training consent",
        "content": "Summarize our Q4 board meeting notes.",
        "headers": {
            "X-AEP-Entity": "org:acme:finance",
            "X-AEP-Classification": "confidential",
            "X-AEP-Consent": "training=no,sharing=org",
            "X-AEP-Budget": "1.00",
            "X-AEP-Sources": "doc:board-minutes-q4",
        },
    },
    {
        "label": "Restricted — minimal consent, tight budget",
        "content": "What is the employee's compensation?",
        "headers": {
            "X-AEP-Entity": "org:acme:hr",
            "X-AEP-Classification": "restricted",
            "X-AEP-Consent": "training=no,sharing=no,retention=30d",
            "X-AEP-Budget": "0.10",
            "X-AEP-Sources": "doc:hr-record-12345",
            "X-AEP-Trace-ID": "trace-abc123",
        },
    },
]

for scenario in SCENARIOS:
    print(f"\n--- {scenario['label']} ---")

    # Show governance headers
    for k, v in scenario["headers"].items():
        print(f"  {k}: {v}")

    r = httpx.post(
        f"{PROXY}/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            **scenario["headers"],
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": scenario["content"]}],
        },
        timeout=30,
    )

    if r.status_code == 400:
        print(f"\n  BLOCKED: {r.json()['error']['message']}")
    else:
        text = r.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"\n  Response: {text[:120]}...")

    # Show AEP response headers
    aep_headers = {k: v for k, v in r.headers.items() if k.lower().startswith("x-aep")}
    if aep_headers:
        for k, v in aep_headers.items():
            print(f"  ← {k}: {v}")

print(f"""
--- Governance protocol ---
  X-AEP-Entity           Who is calling (org, team, user)
  X-AEP-Classification   Data sensitivity: public < internal < confidential < restricted
  X-AEP-Consent          What the data owner allows: training, sharing, retention
  X-AEP-Budget           Maximum spend for this request (USD)
  X-AEP-Trace-ID         Links calls across services for multi-hop audit
  X-AEP-Sources          Which documents/APIs informed this request

  Dashboard: {PROXY.replace('/v1', '/aep/')}
""")
