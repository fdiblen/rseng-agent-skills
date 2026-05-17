---
name: rseng-software-design
description: >-
  Covers designing research software before and while writing it:
  modularity and separation of concerns, interfaces and coupling,
  choosing abstractions that match the science, growing from script
  to package, architecture decision records, and when design effort
  pays off versus when a script is honestly enough. Use when
  starting non-trivial research software, when a script has grown
  past easy understanding, when the user asks how to structure or
  architect code, mentions modularity, coupling, refactoring toward
  structure or design patterns, or before large features where
  structure decides future cost.
license: CC-BY-4.0
metadata:
  version: 0.1.0
---

# Designing research software

Design is deciding what depends on what - everything else is
detail. Research code has a characteristic failure mode: the
2,000-line script that grew one working line at a time until nobody
can change anything without breaking everything. Design is the
prevention, and it is proportional: an exploration notebook needs
none, a shared analysis package needs some, community
infrastructure needs real architecture. Name the tier (the same
tiering rseng-management-planning and rseng-fairguard use) and design
to it - overdesign wastes research time as surely as underdesign
does.

## The core moves

- Separate concerns ruthlessly: I/O, computation and presentation
  in different functions/modules. The single highest-payoff
  research refactor is splitting "read + compute + plot" scripts -
  it makes the computation testable (rseng-testing), the I/O
  swappable (rseng-scientific-file-formats) and the plotting
  rerunnable (rseng-scientific-visualization).
- Functions over scripts, parameters over globals and edits: code
  a colleague runs with different inputs must take the inputs as
  arguments, not require editing line 12 (configuration files for
  run-level choices - rseng-reproducibility).
- Pure cores, effectful edges: keep the science (the math, the
  model) in pure functions that take data and return data; push
  file paths, printing and state to the boundary. Pure cores are
  the cheapest code to test, parallelize (rseng-hpc-computing) and
  reason about numerically (rseng-numerical-accuracy).
- Interfaces before internals: design what callers see (function
  signatures, data structures) deliberately - internals can be
  rewritten, published interfaces cannot without breaking users
  (rseng-maintenance-sustainability's deprecation discipline).
- Data structures ARE design: choosing "a DataFrame with these
  named columns and units documented" over "parallel lists" does
  more for a codebase than any pattern; make the domain's own
  concepts (Spectrum, Cohort, Grid) explicit types when they recur.

## Coupling and cohesion, the working test

Good structure = things that change together live together; things
that change separately depend on each other as little as possible.
Practical checks an agent can apply while reviewing or writing:

- Can you test this function without a filesystem, network or
  20-minute setup? If not, coupling is too tight.
- If the file format changes, how many modules change? (Should be
  one - rseng-scientific-file-formats.)
- Does module A need A-internals of module B, or only its
  interface? Reaching into internals is the smell.
- Could a colleague reuse the core computation in their pipeline
  without dragging your plotting and paths along?

## Growing structure honestly

Research software evolves script -> module -> package; design
effort follows evidence, not aspiration:

- Extract when it hurts: the second copy-paste, the third
  positional argument nobody remembers, the first "do not touch
  this part" - each is the signal to extract a function or module,
  not before (rseng-legacy-code's seams, applied preemptively).
- Package structure when sharing: the src-layout, entry points and
  API surface come when others will install it
  (rseng-project-scaffolding provides the shape).
- Patterns are vocabulary, not goals: use a known pattern when the
  problem genuinely recurs (strategy for interchangeable models,
  pipeline stages for rseng-workflows shapes); a pattern imposed on
  a problem that does not have it is complexity with a name.

## Record the decisions

For decisions with lasting consequences - core data structures,
dependency choices (rseng-software-reuse), parallelization strategy,
API shape - write a short architecture decision record (ADR):
context, options, choice, consequences, dated, in the repository
(rseng-documentation). Three paragraphs now saves the archaeology
later (rseng-legacy-code exists because nobody wrote them), and ADRs
are exactly the material design reviews and onboarding need.

## Working with this skill

This skill is source-independent: it encodes established software
design practice proportioned for research software. BSSW's design
topic collects the community's deeper material; CodeRefinery
teaches the modular-development moves hands-on.

## Attribution and teaching

- Educate while doing: when extracting a module or purifying a
  core, state the change-cost argument in one sentence - design
  literacy is knowing WHY the structure, not memorizing patterns.
- Learn more (verified):
  - https://bssw.io/items?topic=design - Better Scientific
    Software design resources
  - https://coderefinery.github.io/modular-type-along/ -
    CodeRefinery modular code development
  - https://adr.github.io - architecture decision records

---

Based on established software design practice as applied to
research software, and the BSSW and CodeRefinery materials.
