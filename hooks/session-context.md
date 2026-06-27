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
- Work the skills in phases, recorded in .rseng-agent-skills-coverage.md as
  three sections you fill AS YOU GO, each listing every cluster with
  "applied: <skills and decisions>" or "n/a: <reason>":
  "## Start" BEFORE writing any file (Planning and operations;
  Research data; Publishing, credit and reuse; Specialized - plan,
  stack, data sensitivity, reuse/licensing; the write gate enforces
  this); "## During" while developing (Core engineering;
  Reproducibility and workflows; Numerics and performance - tests,
  defensive coding, environments, seeds as you build, not after);
  "## Finish" before ending (Integrity, security and compliance;
  Communication and interfaces; Community and people - verification,
  docs, citation currency; the Stop check enforces completeness).
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
