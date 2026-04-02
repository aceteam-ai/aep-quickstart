#!/usr/bin/env bash
# hosted-proxy.sh — Start AEP proxy for workshop attendees
#
# Runs the proxy with:
# - Pre-loaded API keys (from .env)
# - Gustavo's judge service as sidecar
# - Budget cap per session ($2 default)
# - Exposed via ngrok tunnel (or direct LAN)
#
# Usage:
#   # Load keys and start
#   source .env
#   ./scripts/hosted-proxy.sh
#
#   # With ngrok tunnel
#   ./scripts/hosted-proxy.sh --tunnel
#
#   # Custom budget
#   ./scripts/hosted-proxy.sh --budget 5.00

set -euo pipefail

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
DIM='\033[2m'
NC='\033[0m'

PORT="${AEP_PORT:-8899}"
JUDGE_PORT="${JUDGE_PORT:-5050}"
BUDGET="${BUDGET:-2.00}"
USE_TUNNEL=false
POLICY="policies/clawcamp.yaml"

for arg in "$@"; do
  case "$arg" in
    --tunnel) USE_TUNNEL=true ;;
    --budget=*) BUDGET="${arg#*=}" ;;
    --budget) shift; BUDGET="${1:-2.00}" ;;
    --port=*) PORT="${arg#*=}" ;;
  esac
done

# Check requirements
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo -e "${RED}Error: OPENAI_API_KEY not set. Run: source .env${NC}"
  exit 1
fi

command -v aceteam-aep >/dev/null 2>&1 || {
  echo -e "${RED}Error: aceteam-aep not installed. Run: pip install aceteam-aep[all]${NC}"
  exit 1
}

cleanup() {
  echo -e "\n${DIM}Shutting down...${NC}"
  kill "$PROXY_PID" 2>/dev/null || true
  kill "$JUDGE_PID" 2>/dev/null || true
  kill "$TUNNEL_PID" 2>/dev/null || true
}
trap cleanup EXIT

# Start judge service if available
JUDGE_URL=""
if [ -f "../adaextract2/agentic_safety/judge_service.py" ] || [ -f "../../adanomad/adaextract2/agentic_safety/judge_service.py" ]; then
  JUDGE_SCRIPT=$(find ../adaextract2 ../../adanomad/adaextract2 -name judge_service.py -path '*/agentic_safety/*' 2>/dev/null | head -1)
  if [ -n "$JUDGE_SCRIPT" ]; then
    echo -e "${CYAN}Starting R-Judge service on port $JUDGE_PORT...${NC}"
    python "$JUDGE_SCRIPT" --port "$JUDGE_PORT" --model-name gpt-4o-mini &
    JUDGE_PID=$!
    sleep 2
    JUDGE_URL="http://localhost:$JUDGE_PORT"
    echo -e "${GREEN}Judge service: $JUDGE_URL${NC}"
  fi
else
  JUDGE_PID=0
  echo -e "${YELLOW}Judge service not found — using built-in Trust Engine${NC}"
fi

# Find policy file
if [ ! -f "$POLICY" ]; then
  POLICY=$(find . ../aceteam-aep -name clawcamp.yaml -path '*/policies/*' 2>/dev/null | head -1)
fi

# Start proxy
echo -e "${CYAN}Starting AEP proxy on port $PORT...${NC}"
PROXY_ARGS="proxy --port $PORT --host 0.0.0.0"
if [ -n "$POLICY" ] && [ -f "$POLICY" ]; then
  PROXY_ARGS="$PROXY_ARGS --policy $POLICY"
fi

aceteam-aep $PROXY_ARGS &
PROXY_PID=$!
sleep 3

# Start tunnel if requested
TUNNEL_PID=0
PUBLIC_URL="http://$(hostname -I 2>/dev/null | awk '{print $1}' || echo localhost):$PORT"
if $USE_TUNNEL; then
  if command -v ngrok >/dev/null 2>&1; then
    echo -e "${CYAN}Starting ngrok tunnel...${NC}"
    ngrok http "$PORT" --log=stdout > /tmp/ngrok.log 2>&1 &
    TUNNEL_PID=$!
    sleep 3
    PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null || echo "ngrok failed — check /tmp/ngrok.log")
  else
    echo -e "${YELLOW}ngrok not installed — using LAN IP${NC}"
  fi
fi

echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Workshop Proxy Ready                        ║${NC}"
echo -e "${GREEN}╠══════════════════════════════════════════════╣${NC}"
echo -e "${GREEN}║                                              ║${NC}"
echo -e "${GREEN}║  Attendees run:                              ║${NC}"
echo -e "${GREEN}║  export OPENAI_BASE_URL=$PUBLIC_URL/v1${NC}"
echo -e "${GREEN}║                                              ║${NC}"
echo -e "${GREEN}║  Dashboard: $PUBLIC_URL/aep/${NC}"
echo -e "${GREEN}║  Budget: \$$BUDGET per session                 ║${NC}"
if [ -n "$JUDGE_URL" ]; then
echo -e "${GREEN}║  Judge:  $JUDGE_URL (5 categories)${NC}"
fi
echo -e "${GREEN}║                                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${DIM}Press Ctrl+C to stop${NC}"

wait "$PROXY_PID"
