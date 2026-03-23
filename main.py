"""AEP Quickstart — the four pillars of agent accountability.

Runs all four pillar demos in sequence:
  1. Safety    — PASS / BLOCK enforcement
  2. Cost      — per-call receipts, anomaly detection
  3. Provenance — execution trace across agent hops
  4. Governance — classification, consent, budget via proxy

Usage:
    uv run python main.py            # all pillars
    uv run python main.py --log      # verbose detector output
    uv run python examples/01_safety.py   # individual pillar

Prerequisites:
    1. cp .env.example .env  (add at least one API key)
    2. uv sync
"""

import os
import subprocess
import sys
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

PROXY_PORT = 8099


def run_example(path: str, env: dict | None = None):
    """Run an example script, filtering out HuggingFace background thread noise."""
    full_env = {**os.environ, **(env or {})}
    proc = subprocess.Popen(
        ["uv", "run", "python", path],
        env=full_env,
        stdout=sys.stdout,
        stderr=subprocess.PIPE,
        text=True,
    )
    _, stderr = proc.communicate()
    # Only show stderr lines that aren't HF/safetensors background thread noise
    if stderr:
        for line in stderr.splitlines():
            if any(skip in line for skip in [
                "safetensors", "auto_conversion", "Thread-",
                "get_conversion_pr_reference", "pytorch_model",
                "Traceback", "File ", "self.run()", "self._target",
                "raise e", "raise OSError", "^^^^", "Warning:",
                "huggingface", "HF Hub",
            ]):
                continue
            print(line, file=sys.stderr)
    return proc.returncode


def start_proxy():
    """Start the AEP proxy, wait for it to be ready."""
    proc = subprocess.Popen(
        ["uv", "run", "aceteam-aep", "proxy", "--port", str(PROXY_PORT)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    for _ in range(20):
        time.sleep(0.5)
        try:
            r = httpx.get(f"http://localhost:{PROXY_PORT}/aep/", timeout=2)
            if r.status_code == 200:
                return proc
        except httpx.ConnectError:
            pass
    proc.kill()
    raise RuntimeError("Proxy failed to start")


if __name__ == "__main__":
    # Pillar 1: Safety
    run_example("examples/01_safety.py")

    # Pillar 2: Cost
    print()
    run_example("examples/02_cost.py")

    # Pillar 3: Provenance
    print()
    run_example("examples/03_provenance.py")

    # Pillar 4: Governance (needs proxy)
    print()
    proxy = None
    try:
        print(f"Starting proxy on port {PROXY_PORT} for governance demo...")
        proxy = start_proxy()
        print(f"Dashboard: http://localhost:{PROXY_PORT}/aep/\n")
        run_example("examples/04_governance.py", env={
            "OPENAI_BASE_URL": f"http://localhost:{PROXY_PORT}/v1",
        })
    finally:
        if proxy:
            proxy.terminate()
            proxy.wait(timeout=5)
