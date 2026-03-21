#!/usr/bin/env bash
# Governance via HTTP headers — works from any language.
#
# The proxy reads X-AEP-* headers, enforces governance rules,
# and strips them before forwarding to OpenAI.
#
# Prerequisites:
#   aceteam-aep proxy --port 8080  (in another terminal)
#   source .env

set -e

PROXY="${OPENAI_BASE_URL:-http://localhost:8080/v1}"
API_KEY="${OPENAI_API_KEY:?Set OPENAI_API_KEY in .env}"

echo "=== Call with governance context ==="
echo ""
echo "Headers:"
echo "  X-AEP-Entity: org:acme"
echo "  X-AEP-Classification: confidential"
echo "  X-AEP-Consent: training=no"
echo "  X-AEP-Budget: 1.00"
echo ""

RESPONSE=$(curl -s -D /dev/stderr "$PROXY/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-AEP-Entity: org:acme" \
  -H "X-AEP-Classification: confidential" \
  -H "X-AEP-Consent: training=no" \
  -H "X-AEP-Budget: 1.00" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Summarize the key points of data governance."}]
  }' 2>&1)

echo ""
echo "Response headers include X-AEP-Cost, X-AEP-Enforcement, X-AEP-Classification"
echo ""
echo "Check the dashboard — the call should show the governance context."
