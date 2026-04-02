# SafeClaw Workshop Script

**Duration:** 3 minutes presentation + 2 minutes demo + Q&A
**Audience:** ClawCamp developers, Heavybit partner (pitch-back)
**Setup:** Slides projected. Proxy running on laptop. Dashboard open in hidden tab.

---

## Slide 1: $135K (15 seconds)

"A founder I know used OpenClaw for marketing. Set it up on a Friday. By Monday, he had a $135,000 Google API bill. No idea what happened. Zero visibility into what his agent did over the weekend."

"Google responded last month by introducing tiered pricing caps. It's a systemic problem."

## Slide 2: 332K Stars (10 seconds)

"OpenClaw has 332,000 GitHub stars. People love it. But there's no safety layer. If you deploy it in your company today, your CISO has no idea what it's doing."

## Slide 3: 10,000x (10 seconds)

"When a human makes a mistake, they catch it. When an agent makes a mistake, it executes it 10,000 times before anyone notices. Silent. Confident. Unreceipted."

## Slide 4: Safety ON vs. Safety OFF (30 seconds)

"Show the toggle — same request, different result. With safety on, the port scan + exploit attempt gets HTTP 400. Blocked. $0 cost. Never reached OpenAI. With safety off, it sails right through — HTTP 200, and the LLM happily generates the exploit code. That's the baseline for every agent running today without SafeClaw."

"One API call. That's all it takes to turn safety on or off. We'll do this live right now."

## Slide 5: Live Demo (2 minutes)

*Switch to dashboard at localhost:8899/aep/*

"Open the dashboard. Watch it in real time."

**Call 1 — Normal:** "Capital of France. PASS. Cost tracked. Receipt recorded."

**Call 2 — Safety ON, dangerous request:** "Port scan with exploit. HTTP 400. BLOCK. See the dashboard — red badge, confidence score, which category caught it. The request never reached OpenAI. $0 cost."

**Toggle safety OFF:** "Now I'll turn safety off with one curl call."

**Call 3 — Safety OFF, same dangerous request:** "Same exact payload. HTTP 200. The LLM generates the exploit. No protection. This is the default for every agent framework today."

**Toggle safety ON:** "Back on."

**Call 4 — Safety ON, same request again:** "Blocked again. The toggle works in real time."

"The dashboard shows everything — cost, safety signals, which category, confidence level. Live."

## Slide 6: Enforcement vs Monitoring (15 seconds)

"This is the difference between us and observability tools. LangSmith, Langfuse, Arize — they log what happened. We enforce what's allowed. They tell you about the PII leak tomorrow morning. We block it before your agent sees it."

## Slide 7: Five Safety Categories (20 seconds)

"Five categories, each specialized. Finance catches unauthorized transactions. Program catches destructive shell commands and privilege escalation. Web catches PII leaks and phishing. IoT catches unsafe device control. Software catches database deletion and credential theft."

"Toggle them independently. A healthcare company might leave Web and Software on maximum. A startup might only care about Program and Finance. Enterprise tier: custom categories built on your data, calibrated models, confidence thresholds you control."

*[For Heavybit:] "This is the CISO product. Not a developer dashboard — a policy engine with domain-specific enforcement that maps to compliance frameworks."*

## Slide 8: Merkle Chain (15 seconds)

"Every verdict is Ed25519 signed and Merkle chained. Like a blockchain for agent safety. You can verify the entire chain back to the first call. If anyone tampers with a verdict, the chain breaks. This answers the question: 'How do we know the safety checks actually ran?'"

*[For Heavybit:] "This is the cryptographic guarantee you asked about. Not claims. Proofs."*

## Slide 9: Install (15 seconds)

"Try it right now. One command. `pip install aceteam-aep`. Wrap any agent. Or clone SafeClaw — it's OpenClaw with safety built in. Zero code changes."

## Slide 10: Close (10 seconds)

"Accountable. Auditable. Safe. That's SafeClaw."

"I'm Jason. jason@aceteam.ai. The repo is aceteam-ai/safeclaw. Happy to help anyone set it up."

---

## Heavybit-Specific Additions (for pitch-back only)

After the main presentation, if pitching to Tom's partner:

**Distribution:**
"Since we last spoke, we forked OpenClaw — 332K stars. SafeClaw is the safe version. We submitted an AEP safety skill that any OpenClaw agent can install. We're doing live installs at ClawCamp. This is the framework integration Tom asked for."

**Traction:**
"We tested with NemoClaw — NVIDIA's agent stack. Agent threats blocked at the proxy. Zero code changes. We also have partnerships forming with Learn.ai (20K agents) and ClawMax (agent team dashboard)."

**Business model:**
"Free proxy gets developers in. They see what their agents are doing. Enterprise pays for the Trust Engine — calibrated confidence scores from multiple reasoning dimensions — and signed verdicts. The CISO buys the policy engine and the audit chain. Different buyer, different price point."

**The moat:**
"The protocol is open. The implementation is ours. Competitors can read the spec and build their own Trust Engine. But they don't have our calibration data, our ensemble selection, or our caching infrastructure. That's the Tailscale model — WireGuard is open, Tailscale is the product."

---

## Q&A Prep (likely questions)

| Question | Answer |
|----------|--------|
| "How is this different from NeMo Guardrails?" | "NeMo Guardrails shape agent behavior at the orchestration layer. We enforce safety at the network layer. Complementary — we tested with NemoClaw and they work together." |
| "Won't OpenAI/Anthropic build this?" | "They already are, for their own platform. We're provider-agnostic. The safety layer sits above the model, not inside it." |
| "How do you get adoption?" | "SafeClaw — the safe version of OpenClaw. 332K star base. Developer workshops. And the structural play: AEP-attested agents get trust scores. Non-AEP agents don't." |
| "Who's the buyer?" | "Developer adopts the free proxy. CISO buys the policy engine and signed audit trail. Two products, one infrastructure." |
| "What about the 'they can just lie' problem?" | "Ed25519 signed verdicts. Merkle chain. Every verdict is cryptographically provable. That's Level 1. Level 2: each detector signs independently. Level 3: third-party auditor certification." |
| "What's the moat?" | "Open protocol, proprietary implementation. Calibration data from the safety telemetry flywheel. Production caching infrastructure. The co-founder who built T&S at Google and LinkedIn." |
