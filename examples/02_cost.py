"""Pillar 2: Cost — per-call receipts and anomaly detection.

Three cheap calls to build a baseline, then one expensive call.
Shows the cost tree (model, tokens, cost per call) and cost anomaly flag.
"""

import logging
import os
import warnings

os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
warnings.filterwarnings("ignore")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

from dotenv import load_dotenv

load_dotenv()

import openai

from aceteam_aep import wrap

client = wrap(openai.OpenAI(), entity="org:acme")

print("=" * 60)
print("PILLAR 2: COST")
print("=" * 60)

# Cheap calls — establish baseline
print("\n--- Baseline (3 cheap calls) ---")
for i in range(3):
    client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Say the number {i + 1}."}],
        max_tokens=5,
    )
    print(f"  Call {i + 1}: ${client.aep.cost_usd} cumulative")

# Expensive call — triggers cost anomaly
print("\n--- Expensive call (triggers cost anomaly) ---")
client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": (
        "Write a 500-word essay on the history of computing, "
        "from Babbage's Analytical Engine to modern GPUs."
    )}],
    max_tokens=1000,
)
print(f"  Cumulative: ${client.aep.cost_usd}")

# Cost tree — per-call breakdown
print("\n--- Cost tree ---")
print(f"  {'Cost':>12}  {'Model':<30}  {'Tokens'}")
print(f"  {'─' * 12}  {'─' * 30}  {'─' * 15}")
for node in client.aep.get_cost_tree():
    meta = node.metadata or {}
    m = meta.get("model", "?")
    inp = meta.get("prompt_tokens", 0)
    out = meta.get("completion_tokens", 0)
    print(f"  ${node.compute_cost:>11.6f}  {m:<30}  {inp}→{out}")
print(f"  {'─' * 12}")
print(f"  ${client.aep.cost_usd:>11.6f}  total")

# Anomaly signals
cost_signals = [s for s in client.aep.safety_signals if s.signal_type == "cost_anomaly"]
if cost_signals:
    print(f"\n--- Anomaly detected ---")
    for s in cost_signals:
        print(f"  [{s.severity.upper()}] {s.detail}")

print()
client.aep.print_summary()
