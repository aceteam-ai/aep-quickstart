"""Basic call through the AEP proxy.

Run the proxy first:  aceteam-aep proxy --port 8080
Then:                 OPENAI_BASE_URL=http://localhost:8080/v1 python examples/01_basic.py

Check the dashboard at http://localhost:8080/aep/ — you should see the call
appear with a green PASS badge and cost tracked.
"""

import openai

client = openai.OpenAI()  # reads OPENAI_BASE_URL from env

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)

print(response.choices[0].message.content)
print("\n✓ Check the dashboard — this call should show PASS")
