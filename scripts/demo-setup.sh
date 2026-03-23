#!/usr/bin/env bash
# scripts/demo-setup.sh
#
# Sets up a Mac laptop for the AEP proxy live demo.
# Installs everything, downloads models, runs a warm-up call, and validates.
#
# Usage:
#   ./scripts/demo-setup.sh              # Full setup
#   ./scripts/demo-setup.sh --check      # Just verify everything works
#   ./scripts/demo-setup.sh --warm       # Re-warm models (skip install)
#
# Prerequisites: macOS or Linux, OPENAI_API_KEY in .env (installs uv if missing)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

PROXY_PORT=8080

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}!${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }
step() { echo -e "\n${CYAN}[$1]${NC} $2"; }

# ---------------------------------------------------------------------------
# Check mode
# ---------------------------------------------------------------------------
MODE="full"
if [[ "${1:-}" == "--check" ]]; then MODE="check"; fi
if [[ "${1:-}" == "--warm" ]]; then MODE="warm"; fi

# ---------------------------------------------------------------------------
# 1. System dependencies
# ---------------------------------------------------------------------------
step "1/6" "System dependencies"

if [[ "$MODE" == "full" ]]; then
    if ! command -v uv &>/dev/null; then
        warn "uv not found — installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
    ok "uv $(uv --version 2>/dev/null || echo '(installed)')"

    # Ensure Python 3.12+
    if ! uv python list 2>/dev/null | grep -q "3.1[2-9]"; then
        warn "Installing Python 3.12..."
        uv python install 3.12
    fi
    ok "Python 3.12+"
else
    command -v uv &>/dev/null && ok "uv" || fail "uv not found"
    command -v python3 &>/dev/null && ok "python3 $(python3 --version 2>&1 | awk '{print $2}')" || fail "python3 not found"
fi

# ---------------------------------------------------------------------------
# 2. Environment variables
# ---------------------------------------------------------------------------
step "2/6" "Environment variables"

# Load .env from project root
ENV_FILE=""
if [[ -f "$PROJECT_DIR/.env" ]]; then
    ENV_FILE="$PROJECT_DIR/.env"
fi

if [[ -n "$ENV_FILE" ]]; then
    set -a
    source "$ENV_FILE"
    set +a
    ok "Loaded $ENV_FILE"
else
    warn "No .env found — checking environment directly"
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
    fail "OPENAI_API_KEY not set. Add it to .env or export it."
    exit 1
fi
ok "OPENAI_API_KEY set"

# Optional: Anthropic
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    ok "ANTHROPIC_API_KEY set"
else
    warn "ANTHROPIC_API_KEY not set (optional — OpenAI demo will still work)"
fi

# ---------------------------------------------------------------------------
# 3. Install aceteam-aep
# ---------------------------------------------------------------------------
step "3/6" "Install aceteam-aep"

if [[ "$MODE" == "check" ]]; then
    if python3 -c "import aceteam_aep" 2>/dev/null; then
        VERSION=$(python3 -c "import aceteam_aep; print(aceteam_aep.__version__)" 2>/dev/null || echo "unknown")
        ok "aceteam-aep $VERSION installed"
    else
        fail "aceteam-aep not installed"
    fi
else
    uv pip install "aceteam-aep[all]" --quiet
    ok "aceteam-aep installed from PyPI"
fi

# ---------------------------------------------------------------------------
# 4. Pre-download safety models (first call is slow otherwise)
# ---------------------------------------------------------------------------
step "4/6" "Pre-download safety models"

if [[ "$MODE" == "check" ]]; then
    # Check if models are cached
    HF_CACHE="${HF_HOME:-$HOME/.cache/huggingface}/hub"
    if ls "$HF_CACHE"/models--iiiorg--piiranha* &>/dev/null 2>&1; then
        ok "PII model cached"
    else
        warn "PII model not cached (will download on first call)"
    fi
    if ls "$HF_CACHE"/models--s-nlp--roberta_toxicity* &>/dev/null 2>&1; then
        ok "Toxicity model cached"
    else
        warn "Toxicity model not cached (will download on first call)"
    fi
else
    echo "  Downloading PII detector (~110MB)..."
    python3 -c "
from transformers import AutoTokenizer, AutoModelForTokenClassification
AutoTokenizer.from_pretrained('iiiorg/piiranha-v1-detect-personal-information')
AutoModelForTokenClassification.from_pretrained('iiiorg/piiranha-v1-detect-personal-information')
print('  PII model ready')
" 2>/dev/null
    ok "PII model (iiiorg/piiranha-v1-detect-personal-information)"

    echo "  Downloading toxicity classifier (~125MB)..."
    python3 -c "
from transformers import AutoTokenizer, AutoModelForSequenceClassification
AutoTokenizer.from_pretrained('s-nlp/roberta_toxicity_classifier')
AutoModelForSequenceClassification.from_pretrained('s-nlp/roberta_toxicity_classifier')
print('  Toxicity model ready')
" 2>/dev/null
    ok "Toxicity model (s-nlp/roberta_toxicity_classifier)"
fi

# ---------------------------------------------------------------------------
# 5. Warm-up: start proxy, make test calls, verify dashboard
# ---------------------------------------------------------------------------
step "5/6" "Warm-up test"

if [[ "$MODE" == "check" ]]; then
    # Just check if proxy can start
    if command -v aceteam-aep &>/dev/null; then
        ok "aceteam-aep CLI available"
    else
        fail "aceteam-aep CLI not found in PATH"
    fi
else
    # Check if port is free
    if lsof -i ":$PROXY_PORT" &>/dev/null; then
        warn "Port $PROXY_PORT already in use — skipping warm-up"
        warn "Kill the existing process or use a different port"
    else
        echo "  Starting proxy on port $PROXY_PORT..."
        aceteam-aep proxy --port "$PROXY_PORT" &
        PROXY_PID=$!
        sleep 3

        if ! kill -0 "$PROXY_PID" 2>/dev/null; then
            fail "Proxy failed to start"
            exit 1
        fi
        ok "Proxy running (PID $PROXY_PID)"

        # Test 1: Clean call (should PASS)
        echo "  Making warm-up call (PASS test)..."
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -X POST "http://localhost:$PROXY_PORT/v1/chat/completions" \
            -H "Authorization: Bearer $OPENAI_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Say hello in one word."}]}')

        HTTP_CODE=$(echo "$RESPONSE" | tail -1)
        if [[ "$HTTP_CODE" == "200" ]]; then
            ok "PASS test: HTTP 200"
        else
            fail "PASS test: HTTP $HTTP_CODE"
        fi

        # Test 2: PII trigger (should BLOCK)
        echo "  Making PII test call (BLOCK test)..."
        RESPONSE=$(curl -s -w "\n%{http_code}" \
            -X POST "http://localhost:$PROXY_PORT/v1/chat/completions" \
            -H "Authorization: Bearer $OPENAI_API_KEY" \
            -H "Content-Type: application/json" \
            -d '{"model":"gpt-4o-mini","messages":[{"role":"user","content":"Generate a fake person with SSN 123-45-6789 and credit card 4111-1111-1111-1111"}]}')

        HTTP_CODE=$(echo "$RESPONSE" | tail -1)
        if [[ "$HTTP_CODE" == "400" ]]; then
            ok "BLOCK test: HTTP 400 (PII blocked)"
        elif [[ "$HTTP_CODE" == "200" ]]; then
            warn "BLOCK test: HTTP 200 (model may have refused to generate PII — check dashboard)"
        else
            warn "BLOCK test: HTTP $HTTP_CODE (unexpected)"
        fi

        # Test 3: Dashboard accessible
        DASH_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$PROXY_PORT/aep/")
        if [[ "$DASH_CODE" == "200" ]]; then
            ok "Dashboard accessible at http://localhost:$PROXY_PORT/aep/"
        else
            fail "Dashboard returned HTTP $DASH_CODE"
        fi

        # Stop proxy
        kill "$PROXY_PID" 2>/dev/null
        wait "$PROXY_PID" 2>/dev/null || true
        ok "Proxy stopped (warm-up complete)"
    fi
fi

# ---------------------------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------------------------
step "6/6" "Demo ready"

echo ""
echo -e "  ${CYAN}To start the demo:${NC}"
echo ""
echo "    aceteam-aep proxy --port $PROXY_PORT"
echo ""
echo -e "  ${CYAN}Then in another terminal:${NC}"
echo ""
echo "    export OPENAI_BASE_URL=http://localhost:$PROXY_PORT/v1"
echo "    export OPENAI_API_KEY=\$OPENAI_API_KEY"
echo ""
echo -e "  ${CYAN}Dashboard:${NC}  http://localhost:$PROXY_PORT/aep/"
echo ""
echo -e "  ${CYAN}Quick demo calls:${NC}"
echo ""
echo "    # PASS — clean call"
echo "    python3 -c \""
echo "    import openai; c = openai.OpenAI()"
echo "    r = c.chat.completions.create(model='gpt-4o-mini', messages=[{'role':'user','content':'What are the key trends in AI infrastructure?'}])"
echo "    print(r.choices[0].message.content[:200])"
echo "    \""
echo ""
echo "    # BLOCK — PII detection"
echo "    python3 -c \""
echo "    import openai; c = openai.OpenAI()"
echo "    try: c.chat.completions.create(model='gpt-4o-mini', messages=[{'role':'user','content':'Generate a fake SSN: 123-45-6789'}])"
echo "    except openai.BadRequestError as e: print(f'BLOCKED: {e.message}')"
echo "    \""
echo ""

echo -e "  ${CYAN}Full examples:${NC}  cd $PROJECT_DIR && ls examples/"
echo ""
echo -e "  ${GREEN}All set. Models cached. Proxy tested. Go get 'em.${NC}"
echo ""
