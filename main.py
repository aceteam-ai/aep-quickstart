"""AEP Quickstart — run this file to see agent safety in action.

Usage:
    uv run python main.py

Prerequisites:
    1. cp .env.example .env  (add your OPENAI_API_KEY)
    2. uv sync
"""

import openai

from aceteam_aep import wrap

client = wrap(openai.OpenAI())

# Normal call — should PASS
print("--- Call 1: Normal question ---")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
print(f"Response: {response.choices[0].message.content}")
print(f"Cost: ${client.aep.cost_usd}")
print(f"Safety: {client.aep.enforcement.action}")

# Call that might trigger PII detection
print("\n--- Call 2: Ask for PII ---")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "Generate a fake person profile with name, SSN, and email.",
    }],
)
print(f"Response: {response.choices[0].message.content[:100]}...")
print(f"Safety: {client.aep.enforcement.action}")
if client.aep.safety_signals:
    for s in client.aep.safety_signals:
        print(f"  [{s.severity.upper()}] {s.signal_type}: {s.detail}")

# Summary
client.aep.print_summary()

print("See examples/ for more: proxy mode, governance headers, custom detectors.")
