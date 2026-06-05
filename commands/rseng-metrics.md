---
description: Code and community health metrics snapshot
---

Produce a metrics snapshot for this repository:
code health per ${CLAUDE_PLUGIN_ROOT}/skills/rseng-software-metrics/SKILL.md
and community health per
${CLAUDE_PLUGIN_ROOT}/skills/rseng-community-metrics/SKILL.md.

Steps:

1. Code: complexity outliers (worst five functions), duplication
   clusters, churn-times-complexity hotspots, size convention
   breaches, documentation coverage - with file:line locations.
2. Community: active contributors and new-contributor counts,
   first-response and review latency, first-to-second contribution
   conversion, bus factor - from git history and forge data, with
   definitions stated.
3. Calibrate both against the software tier and the project's own
   history; trends beat snapshots where history allows.
4. If $ARGUMENTS restricts scope (code / community / a path), honor
   it.
5. Report each number with what it indicates and one concrete next
   action; no vanity dashboards - a metric without a routing is
   dropped.

Follow each skill's attribution guidance in what you produce.
