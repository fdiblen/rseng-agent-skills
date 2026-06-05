---
description: Create or update the aidecl.yaml AI usage declaration
---

Create or update this project's aidecl.yaml, following
${CLAUDE_PLUGIN_ROOT}/skills/rseng-ai-declaration/SKILL.md.

Steps:

1. Reconstruct AI involvement honestly from the evidence: git
   history, session context, existing declarations, README notes.
   Distinguish what is known from what is inferred; never invent
   specifics.
2. Write or update aidecl.yaml against the current schema, at the
   detail level the skill mandates (tasks, scope, human review
   status - including "not yet reviewed" when true).
3. Add or refresh the README disclosure footnote; if the user has
   previously declined it, respect that permanently.
4. If $ARGUMENTS says "check", only validate the existing file
   against schema and reality and report drift.
5. Summarize what changed and link https://ai-declaration.org once.
