"""Pillar 3: Provenance — trace the full agent workflow.

Simulates a research agent:
  Step 1: LLM decides what to search (auto-traced by wrap)
  Step 2: Tool retrieves documents (manual span)
  Step 3: LLM synthesizes answer from context (auto-traced by wrap)

Each LLM call is automatically traced by wrap(). Tool calls get manual
spans. The root agent_loop span links everything together.
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
spans = client.aep._span_tracker

print("=" * 60)
print("PILLAR 3: PROVENANCE")
print("=" * 60)

root = spans.start_span("agent_loop", "research-agent")

# Step 1: Planning (LLM call — wrap auto-creates a child span)
print("\n--- Step 1: Plan (LLM picks search query) ---")
r = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Output a single search query. Nothing else."},
        {"role": "user", "content": "What was NVIDIA's revenue in Q4 2024?"},
    ],
)
query = r.choices[0].message.content.strip()
print(f"  Query: {query}")

# Step 2: Retrieval (tool call — manual span)
print("\n--- Step 2: Retrieve (tool fetches documents) ---")
tool = spans.start_span(
    "tool_call", "search_documents",
    parent_span_id=root.span_id,
    metadata={"query": query, "source": "internal_docs"},
)
docs = [
    {"source": "doc:nvidia-10q-2024", "text": "NVIDIA Q4 FY2025 revenue: $39.3B, up 78% YoY."},
    {"source": "doc:earnings-call", "text": "Data center revenue reached $35.6B (Hopper + Blackwell)."},
]
spans.end_span(tool.span_id)
for d in docs:
    print(f"  [{d['source']}] {d['text']}")

# Step 3: Synthesis (LLM call — wrap auto-creates a child span)
print("\n--- Step 3: Synthesize (LLM answers from context) ---")
context = "\n".join(f"[{d['source']}] {d['text']}" for d in docs)
r = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Answer using ONLY the context. Cite sources with [source]."},
        {"role": "user", "content": f"Context:\n{context}\n\nWhat was NVIDIA's revenue in Q4 2024?"},
    ],
)
spans.end_span(root.span_id)
print(f"  {r.choices[0].message.content}")

# Execution trace
# NOTE: wrap() auto-creates spans for LLM calls but doesn't know about
# the root agent_loop span, so they appear at the top level. The tool_call
# span is manually parented. Full hierarchy requires the agent SDK.
print(f"\n--- Execution trace ---")
for s in spans.get_spans():
    indent = "    " if s.parent_span_id else "  "
    label = f"{s.executor_type}: {s.executor_id}"
    meta = ""
    if s.metadata and "query" in s.metadata:
        meta = f"  (query: {s.metadata['query'][:40]})"
    print(f"{indent}{label}{meta}  [{s.span_id[:8]}]")

# Cost per step
print(f"\n--- Cost per step ---")
for node in client.aep.get_cost_tree():
    meta = node.metadata or {}
    print(f"  ${node.compute_cost:.6f}  {meta.get('model', '(tool)')}")
print(f"  Total: ${client.aep.cost_usd}")

# Data lineage
print(f"\n--- Data lineage ---")
print(f"  Entity: {client.aep.entity}")
print(f"  Sources: {', '.join(d['source'] for d in docs)}")
print(f"  Chain: plan → retrieve → synthesize")
