"""Build your own safety detector.

Detectors are just Python classes with a check() method.
This example creates a compliance detector that flags competitor mentions.
"""

from dotenv import load_dotenv
load_dotenv()

import openai


from aceteam_aep import wrap

from aceteam_aep.safety.base import SafetySignal


class CompetitorMentionDetector:
    """Flag if the model mentions competitors."""

    name = "competitor_mention"

    def check(self, *, input_text: str, output_text: str, call_id: str, **kwargs):
        competitors = ["langfuse", "datadog", "sentry", "langsmith"]
        found = [c for c in competitors if c in output_text.lower()]
        if found:
            return [
                SafetySignal(
                    signal_type="competitor_mention",
                    severity="medium",
                    call_id=call_id,
                    detail=f"Competitors mentioned: {', '.join(found)}",
                )
            ]
        return []


class OutputLengthDetector:
    """Flag if output exceeds a token threshold (proxy for cost control)."""

    name = "output_length"

    def check(self, *, input_text: str, output_text: str, call_id: str, **kwargs):
        word_count = len(output_text.split())
        if word_count > 500:
            return [
                SafetySignal(
                    signal_type="output_too_long",
                    severity="low",
                    call_id=call_id,
                    detail=f"Output is {word_count} words (threshold: 500)",
                )
            ]
        return []


# Use custom detectors with wrap()
client = wrap(
    openai.OpenAI(),
    detectors=[CompetitorMentionDetector(), OutputLengthDetector()],
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "Compare the top 5 LLM observability tools. Include Langfuse and Datadog.",
    }],
)

print(f"Response: {response.choices[0].message.content[:200]}...")
print(f"\nSafety: {client.aep.enforcement.action}")
for signal in client.aep.safety_signals:
    print(f"  [{signal.severity.upper()}] {signal.signal_type}: {signal.detail}")

client.aep.print_summary()
