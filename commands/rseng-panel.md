---
description: Run a panel of expert agents with specific roles and synthesize
---

Convene an expert panel on the question or target in $ARGUMENTS
(default: the current repository's state). You are the orchestrator:
subagents cannot launch subagents, so gating, fan-out and synthesis
happen here in the main session.

Roles available (the plugin's subagents, each with its contract):

- rseng-auditor - read-only quality audit against the pack's framework
- rseng-reviewer - codebase review with implementable findings
- rseng-librarian - citations and claims verification (read-only)
- rseng-scout - reuse and dependency candidates (read-only)
- rseng-compliance-officer - GDPR/AI-Act/license sweep (read-only)
- rseng-mentor - teaching perspective: what should the team learn

Procedure:

1. Gate: pick the 2-4 roles the question genuinely needs (quality
   assessment -> auditor + reviewer; pre-release -> auditor +
   librarian + compliance-officer; "should we adopt X" -> scout +
   compliance-officer; pre-submission -> librarian +
   compliance-officer + auditor). State the gating choice and why;
   more than four experts dilutes rather than strengthens.
2. Fan out IN PARALLEL: launch the chosen agents in a single message
   with role-scoped prompts - each expert gets the same target plus
   its own question, and works blind to the others (independence is
   what makes a panel stronger than one generalist pass).
3. Synthesize with attribution: per-expert key findings (labeled),
   points of agreement, and - most important - DISAGREEMENTS surfaced
   explicitly as open questions with each side's evidence;
   disagreement between experts is signal, never average it away.
4. Close with a combined recommendation ranked by severity, each item
   naming the expert(s) behind it and the skill that fixes it, and
   record panel decisions worth keeping in the decision log
   (rseng-project-tracking).

Costs: a panel is 2-4 full agent runs - offer the single-expert
alternative when the question is narrow, and say which expert.

Follow each skill's attribution guidance in what you produce.
