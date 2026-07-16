# Practice enforcement

The hooks under `hooks/` turn the skills from reference material into
enforced practice in Claude Code sessions. This page explains the
protocol they implement, the files they read and write in the user's
project, and how to relax or debug them. For where the hooks sit in
the repository and how their data files are generated, see
[Architecture](architecture.md).

Enforcement is a cooperative guardrail, not containment: it blocks
the normal tool paths and audits the outcome, but a determined agent
or user can route around it. The design goal is that following the
practice is the path of least resistance.

## The phased protocol

Practice work is organized into four phase groups, generated into
`hooks/phases.json` from the cluster map in `skill_directory.py`:

- Start - Planning and operations; Research data; Publishing, credit
  and reuse; Specialized. Considered BEFORE the first file is written:
  plan, stack choice, data sensitivity, reuse and licensing.
- During - Core engineering; Reproducibility and workflows; Numerics
  and performance. Worked while developing, not retrofitted.
- Finish - Integrity, security and compliance; Communication and
  interfaces; Community and people. Verified before the session ends.
- Throughout - a named list of cross-cutting skills (project
  tracking, version-control review, AI declaration, code review,
  honesty, human verification) that stay active for the whole
  session; the Stop audit requires every one of them consulted.

The agent records its pass through these phases in a worklog file,
`.rseng-agent-skills-coverage.md`, at the project root: one section per phase
(`## Start`, `## Throughout`, `## During`, `## Finish`), each listing
every cluster with either `applied: <skills and decisions>` or
`n/a: <one-line reason>`.

## The hook chain

Seven hooks, wired in `hooks/hooks.json` (and mirrored into test

1. SessionStart injects `session-context.md`: the outcome standard,
   the phase protocol, and the artifact floor.
2. UserPromptSubmit runs `phase_status.py`: a one-line live status
   (phase completeness, skills consulted, writes so far, skills
   dispositioned, relevant-but-unconsulted signals) on every prompt.
3. PreToolUse on Skill appends the consulted skill's name to
   `.rseng-agent-skills-usage.log` - the consultation ledger. Coverage claims
   are only believed when backed by this ledger.
4. PreToolUse on Write/Edit runs `gate.py`, the write gate: the first
   project-file write is blocked until the Start and Throughout
   sections of the worklog are complete and ledger-backed; after
   several approved writes the During section falls due as well.
   Writes to `.rseng-agent-skills-*` files always pass (the worklog must be
   writable to satisfy the gate). The gate also counts approved
   writes in `.rseng-agent-skills-writes`.
5. PostToolUse on Skill runs `related_nudge.py`: each consultation
   surfaces the skill's neighbors from `related.json`.
6. PostToolUse on Write/Edit runs `signal_nudge.py`: writing a file
   that matches a relevance signal (a notebook, a CI config, a data
   file...) surfaces the mapped skills the moment they become
   relevant.
7. Stop runs `quality_check.py`, the final audit. It exits silently
   for read-only sessions (zero gated writes). Otherwise it blocks
   the first stop attempt until: the artifact floor is present
   (README, LICENSE, aidecl.yaml, CITATION.cff, tests, an
   environment declaration); all four worklog sections are complete
   with ledger-backed claims; every Throughout skill was consulted;
   Core engineering is applied, not waived; at least five distinct
   skills were consulted; every signal with evidence in the project
   is either consulted or explicitly waived; and every skill in the
   inventory has a disposition. It never blocks twice in a row.

## Relevance signals

`hooks/signals.json` (generated from the `SIGNALS` map in
`skill_directory.py`) maps file patterns and content regexes to the
skills they make mandatory: `*.ipynb` to rseng-notebooks, CI configs to
rseng-ci-cd, `torch`/`sklearn` imports to rseng-fair-ml, seeded
randomness to rseng-defensive-coding, and so on. A matched signal must
end the session either consulted (in the ledger) or waived with
`n/a: <skill> - <reason>` in the worklog. Keep new rules high
precision: a false "relevant" costs every future session a pointless
consultation.

## Files the hooks touch in a user project

- `.rseng-agent-skills-coverage.md` - the phased worklog (agent-written).
- `.rseng-agent-skills-usage.log` - the consultation ledger (hook-written).
- `.rseng-agent-skills-writes` - the approved-write counter (hook-written).
- `.rseng-agent-skills-relaxed` - create this file to disable the gate, the
  status line and the Stop audit entirely. This is the documented
  escape hatch for sessions where enforcement is unwanted.

Advise users to keep these out of version control via
`.git/info/exclude` (or delete them when the work ships); they are
session records, not project content.

## Non-Claude platforms

Other agents have no hook system, so the adapters ship the protocol
as instructions plus `rseng-check/rseng_check.py`, a dependency-free
self-check performing the Stop audit's file-level checks (artifact
floor, worklog completeness, signals, inventory) that the context
files instruct the agent to run before declaring a task complete.
Everything ledger-based is Claude-only; the per-platform status is
tracked in the compatibility overview.

## Debugging and testing

Each hook is a self-contained script reading the hook JSON on stdin;
you can exercise one directly:

    echo '{"tool_name":"Write","tool_input":{"file_path":"x.py"}}' \
      | python3 hooks/gate.py; echo "exit $?"

Exit 2 with a message on stderr is a block; exit 0 passes. The agent
test harness copies these exact files into its sandboxes, so
hook logic, simulate the lifecycle by hand first (fresh project,
worklog written, ledger backing, signal files present) and watch the
messages the agent would see.
