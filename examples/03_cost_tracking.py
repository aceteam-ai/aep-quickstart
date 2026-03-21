"""Cost tracking across multiple calls.

Makes several calls of varying cost. The dashboard shows cumulative spend.
After 3 cheap calls, makes one expensive call — the proxy flags the cost anomaly.
"""

from dotenv import load_dotenv
load_dotenv()

import openai

client = openai.OpenAI()

print("Making 3 cheap calls to establish a baseline...")
for i in range(3):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Say '{i}'"}],
        max_tokens=5,
    )
    print(f"  Call {i + 1}: {response.choices[0].message.content}")

print("\nMaking 1 expensive call (should trigger cost anomaly)...")
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "Write a detailed 500-word essay about the history of computing.",
    }],
    max_tokens=1000,
)
print(f"  Response: {response.choices[0].message.content[:100]}...")

print("\n✓ Check the dashboard:")
print("  - Total cost accumulated across all calls")
print("  - The last call should show a FLAG for cost anomaly (>5x average)")
