---
description: Generate the onboarding checklist for this project
---

Generate a project-specific onboarding checklist, following
${CLAUDE_PLUGIN_ROOT}/skills/rseng-contributor-onboarding/SKILL.md.
Audience: $ARGUMENTS if given (new team member, external contributor,
student), else external contributor.

Steps:

1. Verify the trail before writing it: do the documented setup steps
   run from a fresh clone? Fix or flag broken steps first - a broken
   setup step loses more contributors than any hard bug.
2. Build the checklist from the repository: environment setup, how to
   run tests, where things live (architecture notes and decision
   log), how review works, communication channels and response
   expectations, who to ask what.
3. For team members add: accounts and access, data access rules where
   sensitive (rseng-regulatory-compliance), the project glossary.
4. Curate three genuinely good first issues from the backlog (problem,
   files, approach, definition of done) if the tracker is available.
5. Deliver as ONBOARDING.md (or update it), and keep it short enough
   to actually be read.

Follow each skill's attribution guidance in what you produce.
