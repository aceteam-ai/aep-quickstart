#!/usr/bin/env bash
# scripts/demo-setup.sh
#
# Scaffolding only — installs deps, pre-downloads safety models, verifies env.
# Does NOT run the demo. Run `uv run python main.py` when you're ready.
#
# Usage:
#   ./scripts/demo-setup.sh              # Full setup
#   ./scripts/demo-setup.sh --check      # Verify readiness (no installs)
#
# Prerequisites: macOS or Linux, OPENAI_API_KEY in .env

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}!${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; FAILED=1; }
step() { echo -e "\n${CYAN}[$1]${NC} $2"; }

FAILED=0
MODE="full"
if [[ "${1:-}" == "--check" ]]; then MODE="check"; fi

cd "$PROJECT_DIR"

# ---------------------------------------------------------------------------
# 1. uv
# ---------------------------------------------------------------------------
step "1/4" "System dependencies"

if [[ "$MODE" == "full" ]]; then
    if ! command -v uv &>/dev/null; then
        warn "uv not found — installing..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"
    fi
fi
command -v uv &>/dev/null && ok "uv $(uv --version 2>/dev/null)" || fail "uv not found"

# ---------------------------------------------------------------------------
# 2. .env
# ---------------------------------------------------------------------------
step "2/4" "Environment variables"

if [[ -f "$PROJECT_DIR/.env" ]]; then
    set -a; source "$PROJECT_DIR/.env"; set +a
    ok "Loaded .env"
elif [[ -f "$PROJECT_DIR/.env.example" ]]; then
    fail ".env missing — cp .env.example .env and add your API key"
fi

[[ -n "${OPENAI_API_KEY:-}" ]] && ok "OPENAI_API_KEY" || fail "OPENAI_API_KEY not set"
[[ -n "${ANTHROPIC_API_KEY:-}" ]] && ok "ANTHROPIC_API_KEY" || warn "ANTHROPIC_API_KEY not set (optional)"

# ---------------------------------------------------------------------------
# 3. Python deps
# ---------------------------------------------------------------------------
step "3/4" "Python dependencies"

if [[ "$MODE" == "full" ]]; then
    uv sync
    ok "Dependencies installed"
else
    uv run python -c "import aceteam_aep" 2>/dev/null && ok "aceteam-aep importable" || fail "aceteam-aep not installed"
fi

# ---------------------------------------------------------------------------
# 4. Safety models (delegated to Python)
# ---------------------------------------------------------------------------
step "4/4" "Safety models"

if [[ "$MODE" == "check" ]]; then
    uv run python "$SCRIPT_DIR/warmup.py" --check
else
    uv run python "$SCRIPT_DIR/warmup.py"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
if [[ "$FAILED" -eq 0 ]]; then
    echo -e "  ${GREEN}Ready.${NC} Run the demo:"
    echo "    uv run python main.py"
    echo ""
else
    echo -e "  ${RED}Not ready.${NC} Fix the issues above and re-run."
    exit 1
fi
