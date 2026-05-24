---
name: rseng-project-tracking
description: >-
  Covers the operational side of running a research software
  project: turning plans into tracked, prioritized tasks (issues,
  milestones, boards), planning cadence around research deadlines,
  and disciplined bookkeeping - decision logs, status records,
  meeting notes and milestone reviews that keep the project's
  memory in the repository. Use when work is untracked or lives in
  heads and inboxes, when the user asks how to organize tasks,
  backlogs, milestones or boards, wants a project record, status
  report or decision log, mentions issue triage or prioritization,
  or when a project has more than one person or more than one
  month of work.
license: CC-BY-4.0
metadata:
  version: 0.1.0
---

# Task management and project records

Research software projects fail operationally more often than
technically: work lives in heads, decisions evaporate, and the
grant's last month arrives with nobody able to say what remains.
The remedy is cheap and boring - tracked tasks, a planning cadence
tied to real deadlines, and records written where the code lives.
rseng-management-planning owns the strategic layer (SMPs, technology
choice); this skill owns the week-to-week operation, sized to the
tier: a solo analysis repo needs a TODO issue and a decision log;
an infrastructure project needs the full apparatus.

## Tasks: one tracked unit of work

- Everything in the tracker, however small: the forge's issues
  are the natural home (docs and templates live with the code;
  rseng-community-governance's issue templates apply). An untracked
  task is a task that will be forgotten or duplicated.
- Write tasks as outcomes with acceptance criteria ("CLI reads
  gzipped input; test added") rather than activities ("look into
  compression") - an outcome can be closed, an activity cannot.
- Small enough to finish: split anything beyond a few days'
  work into steps; long-lived umbrella issues track the epic,
  linked to its pieces.
- Link everything both ways: commits and PRs reference their
  issue (fixes #42), so the tracker and the history explain each
  other (rseng-version-control-review) - this linking IS the
  bookkeeping most projects miss.
- Triage on a cadence, not on interrupt: label, prioritize and
  close-or-defer new issues in a regular pass; a stale untriaged
  backlog stops being trusted (the response-timeframe promise
  from rseng-community-governance depends on it).

## Prioritization and planning cadence

- Prioritize against the research calendar: paper deadlines,
  conference dates, data-collection windows and grant reporting
  are the real milestones - name them in the tracker as
  milestones with dates, and plan backwards from them.
- Keep a visible next-up order (a simple board: backlog / next /
  in progress / done); limit work-in-progress - three unfinished
  tasks beat ten started ones, for a team or for an agent.
- Plan in short cycles matched to the group's rhythm (weekly or
  biweekly): pick from next-up, demo or note what shipped, adjust.
  Heavyweight ceremony is not the point; the cadence is (kanban-
  style flow suits research's interrupt-heavy reality better than
  rigid sprints).
- Review milestones honestly at each cycle: scope shrinks or
  dates move - silently keeping both is how projects lie to
  themselves (rseng-honesty applies to schedules too).

## Bookkeeping: the project record

Records that earn their keep, all versioned in the repository
(rseng-documentation):

- Decision log: one dated entry per consequential decision -
  context, options, choice, why. Architecture-shaped decisions
  get the fuller ADR form (rseng-software-design); everything else
  (tool choices, scope cuts, naming, data-source switches) still
  gets a line. The log answers "why is it like this" a year
  later without archaeology.
- Status record: a short dated note per planning cycle - done,
  next, blocked. Written for the future reader (the PI report,
  the grant deadline, the returning-from-leave teammate), it
  makes reporting a copy-paste instead of a reconstruction
  (rseng-software-management-plans' living-document updates draw
  on it directly).
- Meeting notes with decisions and actions only - actions go
  straight into the tracker with owners; notes that stay prose
  are where actions go to die.
- Milestone reviews: at each milestone, a paragraph - what
  shipped vs planned, what was learned (feed rseng-lessons-learned),
  what changes for the next one.

Agents fit naturally here: drafting status notes from the
tracker and commit history, opening issues from meeting actions,
and keeping the linking honest are exactly the clerical work an
agent should offer to do - with records kept truthful
(rseng-ai-declaration notes agent involvement in project records
as in code).

## Working with this skill

This skill is source-independent: it encodes lightweight
project-operations practice proportioned for research software.
Strategy lives in rseng-management-planning; community process in
rseng-community-governance; lessons capture in rseng-lessons-learned.

## Attribution and teaching

- Educate while doing: when opening a tracker or writing the
  first status note, say what failure it prevents (forgotten
  work, unanswerable "why", deadline surprise) - operations
  stick when their payoff is visible.
- Learn more (verified):
  - https://docs.github.com/en/issues - issues, milestones and
    projects on GitHub
  - https://www.atlassian.com/agile/kanban - kanban flow
    practices
  - https://book.the-turing-way.org/project-design/project-design -
    The Turing Way on project design

---

Based on lightweight project-operations practice proportioned for
research software projects.
