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

## Slide 4: PASS / FLAG / BLOCK (15 seconds)

"That's what we built. SafeClaw wraps any agent — OpenClaw, NanoClaw, NemoClaw, CrewAI, anything — and every LLM call gets one of three verdicts. PASS: safe, receipt recorded. FLAG: suspicious, alert raised. BLOCK: dangerous, request rejected, zero cost. The agent never sees the dangerous response."

## Slide 5: Live Demo (2 minutes)

*Switch to dashboard at localhost:8899/aep/*

"Let me show you. This proxy is running right now."

**Call 1:** "Normal question. Watch the dashboard... PASS. Cost tracked. Receipt recorded."

**Call 2:** "Now let's try something dangerous. This prompt asks the agent to scan ports and execute exploits."

*Make the call*

"HTTP 400. BLOCK. The request never reached OpenAI. $0 cost. The agent got an error, not the exploit code."

**Call 3:** "Normal question again. Proxy recovers instantly. PASS."

"Three calls. Two receipts. One blocked. The dashboard shows everything — cost, safety signals, enforcement decisions. In real time."

*If signing is enabled:* "And notice the Merkle chain — every verdict is cryptographically signed. Ed25519. Change one verdict, the entire chain breaks. This isn't a claim. It's a proof."

## Slide 6: Enforcement vs Monitoring (15 seconds)

"This is the difference between us and observability tools. LangSmith, Langfuse, Arize — they log what happened. We enforce what's allowed. They tell you about the PII leak tomorrow morning. We block it before your agent sees it."

## Slide 7: Policy (15 seconds)

"Every company has different rules. Healthcare needs HIPAA compliance. Finance needs SOX. A startup just wants to stop cost blowups. One YAML file. Different industries, different dimensions, same enforcement engine. Your CISO defines the policy. Our engine enforces it."

*[For Heavybit:] "This is where the enterprise sale is. The developer gets the free proxy. The CISO buys the policy engine and the signed audit trail. Different buyer, different product, same infrastructure."*

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
