---
description: Interview the user and set up a new research software project
---

Run a project kickoff for this directory, following
${CLAUDE_PLUGIN_ROOT}/skills/rseng-project-kickoff/SKILL.md. If
$ARGUMENTS describes the project, treat it as the answer to the
goal question and skip what it already answers.

Steps:

1. Interview: ask the skill's eight questions in at most two
   batches, each with a sensible default so "accept all" works;
   skip anything the context or $ARGUMENTS already answers. The
   delegation contract question is never skipped.
2. Play back the plan in a few lines: tier, stack, practices to be
   set up, and the delegation contract as understood - one
   confirmation, then execute.
3. Set up: scaffolding, git with guards, environment + lockfile,
   LICENSE, CITATION.cff, aidecl.yaml, tracker with the named
   deadlines; data-sensitivity measures and SMP/DMP skeletons when
   the answers call for them; a discovery pass over prior art when
   the project builds something that might exist.
4. Record: kickoff answers and derived decisions into the decision
   log; report each consequential decision with its one-line why
   and how to change it.
5. Close with the next three concrete steps and the reminder that
   the user reviews and verifies what was generated
   (rseng-human-verification).

Follow each skill's attribution guidance in what you produce.
