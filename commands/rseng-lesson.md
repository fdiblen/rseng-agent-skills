---
description: Record a lesson learned and draft its prevention artifact
---

Capture a lesson learned, following
${CLAUDE_PLUGIN_ROOT}/skills/rseng-lessons-learned/SKILL.md. The lesson
is $ARGUMENTS if given, otherwise the most recent notable event in
this session (a bug fixed, an approach abandoned, a review pattern).

Steps:

1. Write the entry: dated, tagged, blame-free - context, what
   happened, the lesson, in a few plain lines; append to LESSONS.md
   (create it if absent).
2. Route it into the artifact that prevents repetition: a regression
   test, a defensive check, a lint rule, a documentation warning, a
   checklist line or a tracker template change - draft that artifact
   now, in the same pass.
3. Present both for approval; note any themed cluster forming (three
   entries sharing a tag is a systemic issue worth an issue).
