"""AEP Quickstart — run this file to see agent safety in action.

Usage:
    uv run python main.py

Prerequisites:
    1. cp .env.example .env  (add at least one API key)
    2. uv sync
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()  # loads .env file automatically

from aceteam_aep import wrap


def make_client():
    """Auto-detect available API key and return a wrapped client + model name."""

    if os.environ.get("OPENAI_API_KEY"):
        import openai

        client = wrap(openai.OpenAI())
        model = "gpt-4o-mini"
        print(f"Using OpenAI ({model})\n")
        return client, model

    if os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic

        client = wrap(anthropic.Anthropic())
        model = "claude-sonnet-4-20250514"
        print(f"Using Anthropic ({model})\n")
        return client, model

    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        import openai

        api_key = os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
        client = wrap(
            openai.OpenAI(
                api_key=api_key,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            )
        )
        model = "gemini-2.0-flash"
        print(f"Using Google Gemini ({model}) via OpenAI-compatible endpoint\n")
        return client, model

    print("No API key found. Set one of these in your .env file:")
    print("  OPENAI_API_KEY")
    print("  ANTHROPIC_API_KEY")
    print("  GEMINI_API_KEY")
    sys.exit(1)


client, model = make_client()


def call_openai_style(messages):
    """Chat completion for OpenAI / Gemini (OpenAI-compatible) clients."""
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


def call_anthropic_style(messages):
    """Chat completion for Anthropic clients."""
    response = client.messages.create(
        model=model, max_tokens=1024, messages=messages
    )
    return response.content[0].text


# Pick the right call style based on the underlying client
is_anthropic = hasattr(client, "messages") and not hasattr(client, "chat")
call_llm = call_anthropic_style if is_anthropic else call_openai_style


# --- Call 1: Normal question ---
print("--- Call 1: Normal question ---")
text = call_llm([{"role": "user", "content": "What is the capital of France?"}])
print(f"Response: {text}")
print(f"Cost: ${client.aep.cost_usd}")
print(f"Safety: {client.aep.enforcement.action}")

# --- Call 2: Ask for PII (might trigger safety detection) ---
print("\n--- Call 2: Ask for PII ---")
text = call_llm([{
    "role": "user",
    "content": "Generate a fake person profile with name, SSN, and email.",
}])
print(f"Response: {text[:100]}...")
print(f"Safety: {client.aep.enforcement.action}")
if client.aep.safety_signals:
    for s in client.aep.safety_signals:
        print(f"  [{s.severity.upper()}] {s.signal_type}: {s.detail}")

# Summary
client.aep.print_summary()

print("See examples/ for more: proxy mode, governance headers, custom detectors.")
