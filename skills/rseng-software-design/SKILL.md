---
name: rseng-software-design
description: >-
  Covers designing research software: modularity and separation of concerns,
  interfaces and coupling, growing from script to package, the rule of three
  and the reuse ladder, system-level architecture styles for research systems
  (pipeline, layered, plugin, services), quality-attribute trade-offs,
  C4-style documentation and architecture decision records - and when design
  effort pays off versus when a script is honestly enough. Use when starting
  non-trivial research software, when a script has grown past easy
  understanding, when the user asks how to structure or architect code, or
  mentions modularity, coupling, design patterns or refactoring toward
  structure. For file layout and style see rseng-code-quality; for restructuring
  inherited code see rseng-legacy-code.
license: CC-BY-4.0
metadata:
  version: 0.3.0
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

## Modularity that enables reuse

Reusable code is modular code with its assumptions made explicit -
design for the SECOND user from the start, cheaply:

- The rule of three: generalize on the third use, not the first -
  premature generality is speculative complexity, but the third
  copy-paste is the signal to extract the shared unit
  (rseng-software-metrics' duplication numbers find these).
- Extractable by construction: pure cores with explicit inputs (no
  reads of project-global config inside the science function), no
  hardwired paths, units and conventions documented at the interface
  (rseng-defensive-coding) - the difference between "our script" and
  "a function any colleague can import".
- The reuse ladder: function within the project -> module with its
  own tests -> package others install (rseng-project-scaffolding,
  rseng-software-publishing). Climb when demand exists - a colleague
  asking twice IS demand - and note that well-factored modules are
  what make the strangler and migration paths cheap later
  (rseng-legacy-code, rseng-open-source-migration).
- Do not lock reusable parts to the project: a general-purpose
  reader/solver/plotter that imports project internals cannot leave;
  keep the dependency arrow pointing from project to reusable unit,
  never back.
- Reuse others before designing your own (rseng-software-reuse) - the
  most modular design is the module you did not have to write; and
  when you publish a reusable unit, its interface stability becomes
  a promise (rseng-maintenance-sustainability's deprecation
  discipline).

## Architecture: the system level

When the software is a SYSTEM - multiple components, deployments or
consumers - structure needs deciding above the module level. The
styles that recur in research software, each fitting a shape of
problem:

- Pipeline: stages transforming data in sequence - the natural
  architecture for analysis and processing (rseng-workflows is its
  operational form); keep stages independently runnable with
  explicit intermediate formats (rseng-scientific-file-formats).
- Layered: computation core, orchestration, interface - the
  architecture behind "pure cores, effectful edges" scaled up; the
  core must stay importable without the layers above it (a CLI, a
  notebook and a web UI should share one core).
- Plugin: a stable kernel with extension points - the architecture
  of extensible research tools (analysis frameworks, format
  readers, method registries); invest in it when third parties or
  future-you will add capabilities without touching the kernel
  (rseng-community-governance benefits: contributors write plugins,
  not core patches).
- Services: components behind network interfaces - justified by
  independent scaling, deployment or team boundaries, and paid for
  in operational burden; a research group rarely wants five
  services where one process would do.

Choose by quality attributes, stated out loud: what must this
system do well - throughput (rseng-performance-profiling,
rseng-big-data-processing), portability across laptop and cluster
(rseng-hpc-computing), extensibility, auditability of results
(rseng-provenance)? Architecture is the trade among them; a choice
that cannot name the attribute it serves is fashion. Record the
trade in an ADR (below).

Document the architecture at two zoom levels, C4-style: a context
diagram (the system among its users and neighbors) and a container/
component view (the major pieces and their dependencies) - two
small diagrams that stay updatable beat a mural that rots
(rseng-documentation's developer-notes section is their home).
Re-draw at milestones; a diagram that no longer matches the code
is a review finding (rseng-code-review).

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

Learn more (verified):
  - https://bssw.io/items?topic=design - Better Scientific
    Software design resources
  - https://coderefinery.github.io/modular-type-along/ -
    CodeRefinery modular code development
  - https://adr.github.io - architecture decision records
  - https://c4model.com - the C4 model for architecture diagrams

<!-- related-skills:begin -->

## Related skills

Check whether any of these applies before moving on:

- rseng-documentation - home for ADRs and diagrams
- rseng-hpc-computing - pure cores ease parallelization
- rseng-legacy-code - seams when refactoring existing structure
- rseng-maintenance-sustainability - interface stability and deprecation promises
- rseng-software-reuse - reuse others before designing your own
- rseng-workflows - pipeline style's operational form

<!-- related-skills:end -->
