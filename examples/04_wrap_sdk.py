"""Python SDK — in-process wrapping (no proxy needed).

This is the alternative to the proxy approach. Instead of routing through
a proxy, you wrap your OpenAI client directly in Python.

Both approaches use the same detectors and enforcement.
"""

from dotenv import load_dotenv
load_dotenv()

import openai


from aceteam_aep import wrap

# One line to add safety
client = wrap(openai.OpenAI())

# Use exactly as before
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is 2 + 2?"}],
)

print(f"Response: {response.choices[0].message.content}")
print(f"Cost:     ${client.aep.cost_usd}")
print(f"Safety:   {client.aep.enforcement.action}")
print(f"Calls:    {client.aep.call_count}")
print(f"Signals:  {client.aep.safety_signals}")

# Colored CLI summary
client.aep.print_summary()

# Uncomment to launch the web dashboard:
# client.aep.serve_dashboard()  # http://localhost:8899
