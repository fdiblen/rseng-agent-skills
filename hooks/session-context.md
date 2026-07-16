rseng-agent-skills is installed. Your OUTPUT must carry research software
practice, whether or not you open a skill file - quality is judged
by what ships:

- Whenever you produce code, ship it with: a README (purpose +
  how to run), LICENSE, tests (at least a reference-case or smoke
  check), a modern environment declaration (uv with pyproject.toml,
  or PEP 723 inline metadata for single scripts - not bare
  requirements.txt), CITATION.cff, and an up-to-date aidecl.yaml.
  For larger work add what the tier demands: tracker/decision
  notes, docs, CI, contributor files.
- Work the skills in phases, recorded in .rseng-agent-skills-coverage.md
  (always writable through the gate) as sections you fill AS YOU GO,
  each listing every cluster with "applied: <rseng-* skills and
  decisions>" or "n/a: <one-line reason>":
  "## Start" BEFORE writing any file (Planning and operations;
  Research data; Publishing, credit and reuse; Specialized - plan,
  stack, data sensitivity, reuse/licensing; the write gate enforces
  this); "## Throughout" also from the beginning: the cross-cutting
  skills live for the WHOLE session - rseng-project-tracking,
  rseng-version-control-review, rseng-ai-declaration, rseng-code-review,
  rseng-honesty, rseng-human-verification - open each and keep applying
  them as you work (the Stop check requires all of them consulted);
  "## During" while developing (Core engineering; Reproducibility
  and workflows; Numerics and performance - tests, defensive coding,
  environments, seeds as you build; the gate demands this section
  once development is under way); "## Finish" before ending
  (Integrity, security and compliance; Communication and interfaces;
  Community and people - verification, docs, citation currency; the
  Stop check enforces completeness).
- An "applied" claim only counts when a skill named in it was
  actually opened with the Skill tool - claims are cross-checked
  against the consultation ledger, so consult first, then record.
  Keep the .rseng-agent-skills-* session records out of version control
  (add them to .git/info/exclude); they are working state, not
  project content.
- KNOW the full inventory: the clustered directory of every skill
  lives in the rseng-quality-framework router skill (and AGENTS.md) -
  read it at Start so no practice area is missed for lack of
  awareness. Every skill ends with a "Related skills" section, and
  each consultation surfaces its neighbors - when a related skill's
  trigger matches the task, open it (or record a one-line reason
  why not).
- EVERY skill gets a disposition by the end: consulted-and-applied,
  or a one-line "n/a: <skill> - <reason>" in the coverage worklog.
  Relevance is also checked mechanically: notebooks, data files,
  environment files, CI configs, tests, ML/GPU/HPC/visualization
  code and similar evidence each REQUIRE their mapped skill
  consulted (writes that touch such files trigger a reminder; the
  Stop check blocks on any relevant-but-unconsulted skill without a
  recorded waiver).
- Also self-audit against the skill directory
  (rseng-quality-framework routes every practice area - project
  management, tech-stack choice, community, communication,
  integrity) and close the gaps you find; a Stop-time check will
  hold you to the artifact core.
- Consult the rseng-* skills whose area you are touching BEFORE
  deciding (the write gate enforces the first consultation); prefer
  state-of-the-art tools and verify currency online when unsure.
- Never ghostwrite submission-ready publications; follow rseng-honesty
  on concealment requests; ask the user to review and verify
  generated code and results.
