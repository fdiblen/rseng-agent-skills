"""Skill-relations graph: renders a "Related skills" section into
every SKILL.md and emits hooks/related.json for the consultation
nudge hook.

The map is curated here (single source). Every skill must have an
entry and every edge must name an existing skill - unknown or missing
names fail loudly. Rendering is idempotent (marker block) and must run
as the LAST step after any content regeneration, since source-fed
SKILL.md files are rewritten by the adapter pipeline.
"""

from __future__ import annotations

import json
from pathlib import Path

BEGIN = "<!-- related-skills:begin -->"
END = "<!-- related-skills:end -->"

# skill -> {neighbor: when the neighbor becomes relevant}
RELATED: dict[str, dict[str, str]] = {
    "rseng-agent-security": {
        "rseng-ai-declaration": "disclose agent contributions",
        "rseng-human-verification": "human reviews agent output",
        "rseng-regulatory-compliance": "personal data near agent context",
        "rseng-reproducible-environments": "devcontainers contain the agent",
        "rseng-security": "same principles, project side",
        "rseng-version-control-review": "agent config diffs are security-relevant",
    },
    "rseng-ai-declaration": {
        "rseng-agent-security": "operational counterpart to disclosure",
        "rseng-citation-metadata": "credit and authorship records",
        "rseng-fairguard": "paired default transparency assessment",
        "rseng-honesty": "when disclosure is resisted",
        "rseng-human-verification": "review status feeds the declaration",
        "rseng-regulatory-compliance": "EU AI Act documentation duties",
    },
    "rseng-archiving": {
        "rseng-citation-metadata": "wire DOIs into citation files",
        "rseng-data-management": "domain data repository choice",
        "rseng-legacy-code": "retire path terminates in archive",
        "rseng-maintenance-sustainability": "succession and wind-down archiving",
        "rseng-publishing-releasing": "archive every citable release",
        "rseng-reproducible-environments": "environment capture inside deposits",
    },
    "rseng-big-data-processing": {
        "rseng-green-computing": "distributed runs carry energy cost",
        "rseng-hpc-computing": "job arrays and cluster allocations",
        "rseng-performance-profiling": "profile before scaling out",
        "rseng-scientific-file-formats": "Parquet and chunked stores enable it",
        "rseng-testing": "test transforms on in-memory subsets",
        "rseng-workflows": "restartable pipelines via engines",
    },
    "rseng-ci-cd": {
        "rseng-green-computing": "pipeline energy and runner cost",
        "rseng-hpc-computing": "GPU/HPC runners for heavy jobs",
        "rseng-publishing-releasing": "release automation triggered from CI",
        "rseng-reproducible-environments": "testing inside the shipped container",
        "rseng-security": "secrets management in pipelines",
        "rseng-testing": "what the pipeline should actually run",
    },
    "rseng-citation-hygiene": {
        "rseng-ci-cd": "reference resolution checks in CI",
        "rseng-citation-metadata": "making own software citable",
        "rseng-discovery": "verifying surveyed literature leads",
        "rseng-fact-checking": "verifying non-citation claims",
        "rseng-open-science-practices": "preprint-to-published version links",
        "rseng-research-integrity": "pre-submission verification battery",
    },
    "rseng-citation-metadata": {
        "rseng-archiving": "deposit metadata reuses codemeta",
        "rseng-citation-hygiene": "verifying outbound references",
        "rseng-community-governance": "authorship policy decisions",
        "rseng-fair-software": "metadata implements findability",
        "rseng-publishing-releasing": "DOI minting at release",
        "rseng-software-reuse": "citing adopted software",
        "rseng-version-control-review": "authorship harvested from commit metadata",
    },
    "rseng-code-quality": {
        "rseng-documentation": "docstrings and README quality",
        "rseng-fair-software": "readability serves reusability",
        "rseng-language-guides": "per-language style and tool choice",
        "rseng-legacy-code": "repo-wide reformat cautions",
        "rseng-project-scaffolding": "templates encode this tooling baseline",
        "rseng-software-metrics": "quantifying complexity and duplication",
    },
    "rseng-code-review": {
        "rseng-fairguard": "assessment reruns during milestone reviews",
        "rseng-legacy-code": "characterization tests before implementing fixes",
        "rseng-lessons-learned": "findings become recorded lessons",
        "rseng-project-tracking": "findings become tracked tasks",
        "rseng-quality-framework": "tier calibrates the review bar",
        "rseng-software-metrics": "hotspot map scopes the review",
    },
    "rseng-community-governance": {
        "rseng-citation-metadata": "systematic contributor credit",
        "rseng-community-metrics": "measures the stated promises",
        "rseng-contributor-onboarding": "funnel and first-issue curation",
        "rseng-maintenance-sustainability": "technical side of sustainability",
        "rseng-security": "ownership handover unblocks security response",
        "rseng-user-support": "support channel operations",
    },
    "rseng-community-metrics": {
        "rseng-community-governance": "metrics route to governance actions",
        "rseng-contributor-onboarding": "fixes the funnel leaks found",
        "rseng-maintenance-sustainability": "bus-factor risk response",
        "rseng-management-planning": "grant reports need community evidence",
        "rseng-software-metrics": "same measurement discipline, code side",
        "rseng-user-support": "support load is a signal",
    },
    "rseng-contributor-onboarding": {
        "rseng-community-governance": "rules and CONTRIBUTING newcomers follow",
        "rseng-community-metrics": "measures funnel conversion",
        "rseng-pair-programming": "kind first-PR review bar",
        "rseng-reproducible-environments": "fresh-clone dev setup must work",
        "rseng-trainer": "teaching cohorts and students",
        "rseng-user-support": "active answerers become contributors",
    },
    "rseng-data-management": {
        "rseng-archiving": "long-term data deposit",
        "rseng-citation-metadata": "data DOIs and two-way citation",
        "rseng-data-management-plans": "funder plan over the practice",
        "rseng-regulatory-compliance": "sensitive and personal data obligations",
        "rseng-scientific-file-formats": "choosing and engineering the format",
        "rseng-workflows": "scripted regeneration of derived data",
    },
    "rseng-data-management-plans": {
        "rseng-archiving": "deposit and preservation promises",
        "rseng-data-management": "the practice the plan describes",
        "rseng-licensing": "data license choices in the plan",
        "rseng-management-planning": "SMP twin, shared drafting cadence",
        "rseng-regulatory-compliance": "GDPR, consent and anonymization sections",
        "rseng-scientific-file-formats": "naming open formats deliberately",
    },
    "rseng-debugging": {
        "rseng-defensive-coding": "make silent bugs crash first",
        "rseng-hpc-computing": "scale-dependent cluster-only failures",
        "rseng-lessons-learned": "postmortems from debugging trails",
        "rseng-numerical-accuracy": "deciding whether divergence is real",
        "rseng-reproducible-environments": "pin environment to reproduce the bug",
        "rseng-workflows": "cached stages make pipeline bisection cheap",
    },
    "rseng-defensive-coding": {
        "rseng-big-data-processing": "quarantine-and-log at batch scale",
        "rseng-data-management": "data dictionaries the schemas enforce",
        "rseng-hpc-computing": "per-worker RNG streams in parallel jobs",
        "rseng-numerical-accuracy": "float behavior behind silent errors",
        "rseng-research-integrity": "post-hoc hunt for same failures",
        "rseng-testing": "fired checks become regression tests",
    },
    "rseng-dependency-management": {
        "rseng-ci-cd": "tests absorb automated update PRs",
        "rseng-license-compliance": "license axis analysis",
        "rseng-maintenance-sustainability": "upstream bus-factor and succession signals",
        "rseng-reproducible-environments": "pinning and lockfiles",
        "rseng-security": "vulnerabilities, SBOM, supply chain signals",
        "rseng-software-reuse": "candidates entering the intake gate",
    },
    "rseng-discovery": {
        "rseng-citation-hygiene": "verifying surveyed references",
        "rseng-dependency-management": "vetting discovered software",
        "rseng-fact-checking": "verifying claims before repeating them",
        "rseng-science-communication": "related-work narrative for audiences",
        "rseng-software-peer-review": "state-of-field for JOSS paper",
        "rseng-software-reuse": "candidate fit and citation duty",
    },
    "rseng-documentation": {
        "rseng-citation-metadata": "CITATION.cff beside the README",
        "rseng-licensing": "LICENSE file guidance",
        "rseng-science-communication": "outward papers and announcements",
        "rseng-storytelling": "narrative for broad audiences",
        "rseng-user-support": "recurring questions become docs",
        "rseng-ux-accessibility": "docs readability and accessibility",
    },
    "rseng-fact-checking": {
        "rseng-citation-hygiene": "existence check runs first",
        "rseng-documentation": "README claims need the same bar",
        "rseng-honesty": "when asked to fake support",
        "rseng-open-science-practices": "preprint status labeling",
        "rseng-research-integrity": "document-level pre-submission battery",
        "rseng-testing": "executable checks beat document claims",
    },
    "rseng-fair-ml": {
        "rseng-archiving": "DOIs for model and dataset snapshots",
        "rseng-data-management": "dataset documentation beneath Croissant",
        "rseng-fair-software": "the general FAIR baseline",
        "rseng-gpu-computing": "hardware requirements for model reuse",
        "rseng-licensing": "licensing weights and training data",
        "rseng-reproducibility": "model cards written from actual runs",
    },
    "rseng-fair-software": {
        "rseng-archiving": "accessibility beyond active development",
        "rseng-citation-metadata": "metadata and identifiers implement findability",
        "rseng-fair-ml": "FAIR extended to ML artifacts",
        "rseng-fairguard": "automated FAIR4RS scoring",
        "rseng-licensing": "license implements reusability",
        "rseng-software-reuse": "registering software for findability",
    },
    "rseng-fairguard": {
        "rseng-ai-declaration": "transparency pair per pack default",
        "rseng-ci-cd": "wiring the quality gate",
        "rseng-citation-metadata": "fixing metadata findings",
        "rseng-fair-software": "concepts behind the indicators",
        "rseng-licensing": "fixing license findings",
        "rseng-publishing-releasing": "fixing release and archive findings",
    },
    "rseng-gpu-computing": {
        "rseng-green-computing": "accelerator energy efficiency matching",
        "rseng-hpc-computing": "running GPU jobs on clusters",
        "rseng-numerical-accuracy": "float32 precision consequences",
        "rseng-performance-profiling": "verify GPU is warranted first",
        "rseng-reproducible-environments": "driver and toolkit pinning",
        "rseng-testing": "CPU reference path for correctness",
    },
    "rseng-green-computing": {
        "rseng-ci-cd": "lean pipelines waste less compute",
        "rseng-data-management": "storage retention has a footprint",
        "rseng-gpu-computing": "matching hardware to workload efficiency",
        "rseng-hpc-computing": "right-sized resource requests save energy",
        "rseng-performance-profiling": "speedups cut energy roughly proportionally",
        "rseng-workflows": "caching avoids recomputing pipeline stages",
    },
    "rseng-honesty": {
        "rseng-ai-declaration": "honest disclosure mechanics",
        "rseng-citation-metadata": "authorship reflects real contribution",
        "rseng-human-verification": "unverified must not claim verified",
        "rseng-research-integrity": "fabricated results have detection context",
        "rseng-storytelling": "tell the honest story well",
        "rseng-version-control-review": "clean history forward, never rewrite",
    },
    "rseng-hpc-computing": {
        "rseng-big-data-processing": "distributed data framework path",
        "rseng-data-management": "staging data across cluster filesystems",
        "rseng-green-computing": "honest requests save energy",
        "rseng-performance-profiling": "measure scaling before allocating",
        "rseng-reproducible-environments": "containers and pinned modules",
        "rseng-workflows": "sweeps via workflow engines",
    },
    "rseng-human-verification": {
        "rseng-ai-declaration": "record review status honestly",
        "rseng-code-review": "structured review lenses",
        "rseng-numerical-accuracy": "spot-check numeric assumptions",
        "rseng-pair-programming": "division of labor with agent",
        "rseng-reproducibility": "rerun the pipeline from clean",
        "rseng-testing": "run and read the assertions",
    },
    "rseng-language-guides": {
        "rseng-code-quality": "linter and formatter per ecosystem",
        "rseng-dependency-management": "verifying current ecosystem tooling",
        "rseng-management-planning": "language choice for new projects",
        "rseng-notebooks": "Python/Julia notebook practice",
        "rseng-project-scaffolding": "language templates at kickoff",
        "rseng-testing": "per-language test framework choice",
    },
    "rseng-legacy-code": {
        "rseng-archiving": "retire path ends in archive",
        "rseng-documentation": "recording recovered intent",
        "rseng-open-source-migration": "commercial-platform exits build on this",
        "rseng-reproducible-environments": "capture the working environment first",
        "rseng-testing": "characterization test mechanics",
        "rseng-version-control-review": "small reversible cleanup commits",
    },
    "rseng-lessons-learned": {
        "rseng-code-quality": "review-pattern lessons become lint rules",
        "rseng-debugging": "bug fix evidence drafts the lesson",
        "rseng-documentation": "gotcha lessons become doc warnings",
        "rseng-project-tracking": "postmortem actions get tracked owners",
        "rseng-testing": "bug lessons become regression tests",
        "rseng-trainer": "lessons become tomorrow's teaching material",
    },
    "rseng-license-compliance": {
        "rseng-ci-cd": "policy-as-code license gates",
        "rseng-community-governance": "CLA implications of dual licensing",
        "rseng-dependency-management": "license axis of intake vetting",
        "rseng-licensing": "first license choice basics",
        "rseng-publishing-releasing": "notice obligations at release",
        "rseng-security": "SBOM carries license data",
    },
    "rseng-licensing": {
        "rseng-citation-metadata": "SPDX id in metadata files",
        "rseng-data-management": "licensing datasets alongside code",
        "rseng-fair-ml": "licensing model weights",
        "rseng-fair-software": "license implements reusability",
        "rseng-license-compliance": "dependency audits and enforcement",
        "rseng-open-source-migration": "licensing freed code",
    },
    "rseng-maintenance-sustainability": {
        "rseng-archiving": "retiring software needs archival deposit",
        "rseng-ci-cd": "scheduled runs catch external breakage",
        "rseng-code-quality": "incremental refactoring and static analysis",
        "rseng-contributor-onboarding": "recruiting community maintenance help",
        "rseng-dependency-management": "dependency update and audit mechanics",
        "rseng-green-computing": "footprint review at maintenance cadence",
    },
    "rseng-management-planning": {
        "rseng-archiving": "preservation promises need archiving mechanics",
        "rseng-data-management-plans": "drafting the data twin plan",
        "rseng-licensing": "plan's licensing section needs specifics",
        "rseng-maintenance-sustainability": "planning the long-term maintenance section",
        "rseng-project-kickoff": "brand-new project starts with interview",
        "rseng-project-scaffolding": "template kickstart after language choice",
    },
    "rseng-notebooks": {
        "rseng-hpc-computing": "papermill batch sweeps on clusters",
        "rseng-reproducibility": "executed notebooks as deliberate result records",
        "rseng-science-communication": "narrative layer of analysis notebooks",
        "rseng-scientific-visualization": "figure-producing notebook cells",
        "rseng-trainer": "notebooks as teaching material",
        "rseng-version-control-review": "jupytext twins make diffs reviewable",
    },
    "rseng-numerical-accuracy": {
        "rseng-debugging": "diagnosing cross-platform result differences",
        "rseng-gpu-computing": "float32 and mixed precision trade-offs",
        "rseng-legacy-code": "characterization-test tolerance sign-off",
        "rseng-performance-profiling": "precision changes as deliberate optimization",
        "rseng-reproducible-environments": "pinned libraries limit result drift",
        "rseng-testing": "tolerance-based numerical test design",
    },
    "rseng-open-science-practices": {
        "rseng-archiving": "both-ways artifact linking discipline",
        "rseng-citation-hygiene": "preprint-to-published version drift",
        "rseng-publishing-releasing": "citable code release behind claims",
        "rseng-regulatory-compliance": "governs the closed components",
        "rseng-research-integrity": "preregistration deviations reported honestly",
        "rseng-software-peer-review": "open review practices transfer",
    },
    "rseng-open-source-migration": {
        "rseng-legacy-code": "characterization tests and strangler pattern",
        "rseng-licensing": "license the freed code",
        "rseng-numerical-accuracy": "parity tolerances across platforms",
        "rseng-reproducible-environments": "target-ecosystem pinning as you go",
        "rseng-scientific-file-formats": "exporting proprietary data formats first",
        "rseng-software-reuse": "adopt an existing open reimplementation",
    },
    "rseng-pair-programming": {
        "rseng-agent-security": "agent never approves its own work",
        "rseng-ai-declaration": "recording agent collaboration honestly",
        "rseng-research-integrity": "evidence questions at review time",
        "rseng-testing": "ping-pong TDD produces the suite",
        "rseng-trainer": "narrated pairing is the teaching channel",
        "rseng-version-control-review": "small commits during sessions",
    },
    "rseng-performance-profiling": {
        "rseng-big-data-processing": "memory-bound escalation path",
        "rseng-ci-cd": "benchmark regression tracking in CI",
        "rseng-gpu-computing": "GPU port only after profiling evidence",
        "rseng-green-computing": "speedups cut energy proportionally",
        "rseng-hpc-computing": "scaling curves before big allocations",
        "rseng-numerical-accuracy": "tolerances when optimizations shift results",
    },
    "rseng-project-kickoff": {
        "rseng-data-management": "data questions route here early",
        "rseng-discovery": "prior-art pass before building",
        "rseng-management-planning": "SMP skeleton after kickoff answers",
        "rseng-project-scaffolding": "executes the scaffolding step",
        "rseng-project-tracking": "hands over steady-state operation",
        "rseng-quality-framework": "tier classification calibrates all defaults",
    },
    "rseng-project-scaffolding": {
        "rseng-ci-cd": "generated workflow files need understanding",
        "rseng-citation-metadata": "template ships CITATION.cff and cffconvert check",
        "rseng-dependency-management": "keeping generated tooling current",
        "rseng-fair-software": "templates encode the FAIR baseline",
        "rseng-project-kickoff": "management-side project start",
        "rseng-publishing-releasing": "packaging and release setup follow-up",
    },
    "rseng-project-tracking": {
        "rseng-ai-declaration": "disclosing AI-drafted project records",
        "rseng-community-governance": "issue templates and triage promises",
        "rseng-honesty": "honest schedules and visible scope cuts",
        "rseng-lessons-learned": "milestone reviews feed lessons capture",
        "rseng-management-planning": "strategic plan the tracker executes",
        "rseng-version-control-review": "linking commits and PRs to issues",
    },
    "rseng-provenance": {
        "rseng-ai-declaration": "agents are PROV Agents too",
        "rseng-archiving": "RO-Crate is the deposit shape",
        "rseng-data-management": "dataset versions and checksums in records",
        "rseng-honesty": "stated gaps beat invented links",
        "rseng-reproducibility": "same promise at a different layer",
        "rseng-scientific-file-formats": "embedded origin metadata in files",
    },
    "rseng-publishing-releasing": {
        "rseng-archiving": "preservation follows each release",
        "rseng-ci-cd": "release automation pipelines",
        "rseng-citation-metadata": "DOI and CITATION.cff at release",
        "rseng-legacy-code": "retire path needs tagged archive",
        "rseng-license-compliance": "notice obligations at release time",
        "rseng-software-publishing": "channel craft after cutting release",
    },
    "rseng-quality-framework": {
        "rseng-fair-software": "FAIRness dimension practice",
        "rseng-fairguard": "FAIR assess-fix-reassess sibling loop",
        "rseng-management-planning": "tier drives plan rigor",
        "rseng-project-kickoff": "new projects pair tiering with interview",
        "rseng-software-metrics": "quantitative indicator measurement",
        "rseng-testing": "most common first unmet indicator",
    },
    "rseng-regulatory-compliance": {
        "rseng-ai-declaration": "seeds AI Act documentation trail",
        "rseng-archiving": "publishing datasets triggers obligations",
        "rseng-data-management": "sensitive-data storage and stewardship",
        "rseng-fair-ml": "training-data documentation duties",
        "rseng-security": "encryption, access control, leak response",
        "rseng-testing": "robustness evidence for AI Act",
    },
    "rseng-reproducibility": {
        "rseng-ai-declaration": "declaring AI involvement in results",
        "rseng-archiving": "depositing the package with a DOI",
        "rseng-data-management": "versioned data with checksums",
        "rseng-numerical-accuracy": "stating expected run-to-run variability",
        "rseng-publishing-releasing": "tagged frozen release for the package",
        "rseng-software-peer-review": "CODECHECK-style independent reruns",
    },
    "rseng-reproducible-environments": {
        "rseng-dependency-management": "pinning policy and update cadence",
        "rseng-hpc-computing": "Apptainer on clusters without root",
        "rseng-legacy-code": "running old code in isolated environments",
        "rseng-notebooks": "kernel environments belong in lockfiles",
        "rseng-security": "scanning images and pinned dependencies",
        "rseng-workflows": "per-step environments in pipelines",
    },
    "rseng-research-integrity": {
        "rseng-ai-declaration": "declarations complete at submission",
        "rseng-archiving": "availability statements must resolve",
        "rseng-citation-hygiene": "reference existence and retraction screens",
        "rseng-fact-checking": "do sources support the claims",
        "rseng-numerical-accuracy": "numeric mismatches may be float issues",
        "rseng-reproducibility": "regenerate numbers from the pipeline",
    },
    "rseng-science-communication": {
        "rseng-citation-metadata": "DOIs and citable releases",
        "rseng-documentation": "README is the landing page",
        "rseng-fact-checking": "fact-check the draft claims",
        "rseng-publishing-releasing": "announcements draft from changelogs",
        "rseng-software-peer-review": "venue mechanics and review prep",
        "rseng-storytelling": "narrative spine for broad audiences",
    },
    "rseng-scientific-file-formats": {
        "rseng-big-data-processing": "chunked stores enable scalable reads",
        "rseng-data-management": "surrounding dataset practice and deposit",
        "rseng-fair-software": "domain standards serve interoperability",
        "rseng-legacy-code": "schema versioning and old-format readers",
        "rseng-numerical-accuracy": "round-trip tests need float tolerances",
        "rseng-testing": "golden-file and compatibility tests",
    },
    "rseng-scientific-visualization": {
        "rseng-hpc-computing": "parallel rendering and in-situ output",
        "rseng-reproducibility": "regenerable figures from scripts",
        "rseng-science-communication": "framing figures for talks and papers",
        "rseng-scientific-file-formats": "mesh and volume data layouts",
        "rseng-ux-accessibility": "colorblind-safe maps and annotations",
        "rseng-workflows": "figures regenerate inside pipelines",
    },
    "rseng-security": {
        "rseng-agent-security": "least-privilege applied to the agent",
        "rseng-ci-cd": "hardening CI tokens and workflows",
        "rseng-dependency-management": "vetting and updating dependencies",
        "rseng-publishing-releasing": "signed releases, SBOMs, provenance",
        "rseng-regulatory-compliance": "personal data raises legal duties",
        "rseng-reproducible-environments": "lockfiles pin the supply chain",
    },
    "rseng-software-design": {
        "rseng-documentation": "home for ADRs and diagrams",
        "rseng-hpc-computing": "pure cores ease parallelization",
        "rseng-legacy-code": "seams when refactoring existing structure",
        "rseng-maintenance-sustainability": "interface "
        "stability and "
        "deprecation "
        "promises",
        "rseng-software-reuse": "reuse others before designing your own",
        "rseng-workflows": "pipeline style's operational form",
    },
    "rseng-software-metrics": {
        "rseng-community-metrics": "project-level counterpart to code metrics",
        "rseng-documentation": "doc-coverage is its measurable slice",
        "rseng-legacy-code": "hotspot map targets refactoring",
        "rseng-maintenance-sustainability": "trend tracking signals sustainability risk",
        "rseng-quality-framework": "supplies the quantitative half of assessments",
        "rseng-software-design": "coupling numbers test the design",
    },
    "rseng-software-peer-review": {
        "rseng-ai-declaration": "JOSS asks about AI use",
        "rseng-citation-metadata": "CITATION.cff and DOI at acceptance",
        "rseng-discovery": "state-of-the-field section material",
        "rseng-reproducible-environments": "clean-room installs for reviewing",
        "rseng-software-publishing": "JOSS within the channel mix",
        "rseng-version-control-review": "PR-level review is distinct",
    },
    "rseng-software-publishing": {
        "rseng-ci-cd": "trusted publishing from CI",
        "rseng-citation-metadata": "registries harvest CITATION.cff/codemeta",
        "rseng-project-scaffolding": "installable package structure",
        "rseng-publishing-releasing": "release mechanics behind each channel",
        "rseng-reproducible-environments": "fresh-install verification clean room",
        "rseng-software-peer-review": "JOSS submission pathway",
    },
    "rseng-software-reuse": {
        "rseng-citation-metadata": "citing adopted software",
        "rseng-dependency-management": "intake vetting of candidates",
        "rseng-discovery": "broad landscape survey first",
        "rseng-fair-software": "being findable yourself",
        "rseng-lessons-learned": "recording build-vs-reuse decisions",
        "rseng-open-source-migration": "adoption instead of porting",
    },
    "rseng-storytelling": {
        "rseng-ai-declaration": "disclose AI-assisted storytelling",
        "rseng-community-governance": "consent and recognition habits",
        "rseng-data-management": "truthful data practices in stories",
        "rseng-science-communication": "research-facing communication mechanics",
        "rseng-scientific-visualization": "honest figures for lay audiences",
        "rseng-ux-accessibility": "alt text and plain language",
    },
    "rseng-testing": {
        "rseng-ci-cd": "running the suite on every push",
        "rseng-debugging": "every fix becomes a regression test",
        "rseng-defensive-coding": "runtime checks become test assertions",
        "rseng-green-computing": "budgeting energy cost of full matrices",
        "rseng-legacy-code": "characterization tests before changing inherited code",
        "rseng-numerical-accuracy": "choosing tolerances for numerical assertions",
    },
    "rseng-trainer": {
        "rseng-agent-security": "teaching responsible AI-assisted coding",
        "rseng-contributor-onboarding": "cohort and student onboarding",
        "rseng-documentation": "tutorials and lesson material",
        "rseng-lessons-learned": "captured lessons become curriculum",
        "rseng-pair-programming": "teaching inside collaborative sessions",
        "rseng-quality-framework": "priority order for teaching topics",
    },
    "rseng-user-support": {
        "rseng-community-metrics": "first-response time is the metric",
        "rseng-contributor-onboarding": "answerers are future contributors",
        "rseng-debugging": "reproduce user-reported bugs first",
        "rseng-documentation": "answers become FAQ entries",
        "rseng-project-tracking": "requests and load feed planning",
        "rseng-ux-accessibility": "error messages causing the questions",
    },
    "rseng-ux-accessibility": {
        "rseng-defensive-coding": "humane fail-loud error messages",
        "rseng-documentation": "docs accessibility and help parity",
        "rseng-science-communication": "accessible slides and figures",
        "rseng-scientific-visualization": "colorblind-safe honest palettes",
        "rseng-testing": "golden-file tests on CLI ergonomics",
        "rseng-user-support": "error-message questions reveal UX gaps",
    },
    "rseng-version-control-review": {
        "rseng-ci-cd": "CI gating merges before human review",
        "rseng-citation-metadata": "commit metadata feeds contributor credit",
        "rseng-contributor-onboarding": "review as an onboarding channel",
        "rseng-data-management": "DVC/git-annex for large data files",
        "rseng-notebooks": "jupytext twins make notebook diffs reviewable",
        "rseng-publishing-releasing": "tags marking published versions",
        "rseng-software-peer-review": "CODECHECK-style heavier review of paper code",
    },
    "rseng-workflows": {
        "rseng-big-data-processing": "scaling pipelines across many datasets",
        "rseng-discovery": "finding reusable workflows in registries",
        "rseng-fair-software": "FAIR principles applied to workflows",
        "rseng-hpc-computing": "running stages on clusters",
        "rseng-provenance": "engine logs are provenance capture",
        "rseng-reproducible-environments": "per-step pinned environments",
    },
}


def _block(related: dict[str, str]) -> str:
    lines = [
        BEGIN,
        "",
        "## Related skills",
        "",
        "Check whether any of these applies before moving on:",
        "",
    ]
    lines += [f"- {name} - {reason}" for name, reason in related.items()]
    lines += ["", END]
    return "\n".join(lines)


def render(repo_root: Path) -> None:
    # Take the universe from disk, not from CLUSTERS. Deriving it from the
    # cluster map meant a skill missing from BOTH maps was invisible to this
    # assertion: it rendered "sections for 67 skills", exited 0, and left the
    # new one with no related-skills block and no entry in related.json.
    # Three documents promise this fails loudly; now it does.
    known = {p.parent.name for p in (repo_root / "skills").glob("rseng-*/SKILL.md")}
    missing = sorted(known - set(RELATED))
    assert not missing, f"skills without a RELATED entry: {missing}"
    unknown = sorted(set(RELATED) - known)
    assert not unknown, f"RELATED names unknown skills: {unknown}"
    for skill, related in RELATED.items():
        bad = sorted(set(related) - known)
        assert not bad, f"{skill}: unknown neighbors {bad}"
        assert skill not in related, f"{skill}: self-edge"
        path = repo_root / "skills" / skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        block = _block(related)
        if BEGIN in text:
            head, rest = text.split(BEGIN, 1)
            _, tail = rest.split(END, 1)
            text = head + block + tail
        else:
            anchor = "\n---\n\nGuidance based on"
            if anchor in text:
                head, tail = text.split(anchor, 1)
                text = head.rstrip() + "\n\n" + block + "\n" + anchor + tail
            else:
                text = text.rstrip() + "\n\n" + block + "\n"
        path.write_text(text, encoding="utf-8")
    (repo_root / "hooks" / "related.json").write_text(
        json.dumps(RELATED, indent=2) + "\n", encoding="utf-8"
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    render(repo_root)
    print(f"related-skills sections rendered for {len(RELATED)} skills")


if __name__ == "__main__":
    main()
