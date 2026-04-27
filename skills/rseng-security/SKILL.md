---
name: rseng-security
description: >-
  Covers securing research software and its supply chain: secrets
  hygiene and leak response, dependency vulnerability scanning and
  pinning, OpenSSF Scorecard and Best Practices badge, SLSA provenance
  levels, SBOMs, signed releases and repository hardening. Use
  PROACTIVELY when setting up CI or releases for research software,
  when credentials or tokens appear in code or history, when the user
  asks how secure their project or dependencies are, mentions
  Scorecard, SLSA, SBOM, CVEs or secret scanning, or handles data that
  makes the software a target.
license: CC-BY-4.0
metadata:
  version: 0.1.0
---

# Security for research software

Research software is unusually exposed: long-lived unmaintained
dependencies, credentials for shared clusters and data services, and
code that outlives its authors. A 2025 study scoring 3,248 research
repositories with OpenSSF Scorecard found an average of 3.5/10 - the
gap is the norm, not the exception. Security here is mostly hygiene,
not cryptography: a handful of repeatable practices prevent the
common failures.

## Secrets hygiene (the non-negotiable)

- Never commit credentials, tokens, private keys or connection
  strings - not even briefly; git history is forever and forges cache
  aggressively.
- Guard rails BEFORE the first secret exists: .gitignore entries for
  env files, a secret scanner (gitleaks) in pre-commit and CI.
- Configuration via environment variables or untracked local files;
  document required variables in the README with dummy values.
- If a secret lands in history: revoke and rotate it FIRST (assume it
  is compromised the moment it is pushed), then clean history if the
  repository is private enough for that to matter. Rotation is the
  fix; history rewriting is cosmetics.

## Dependencies and the supply chain

- Pin dependencies with lockfiles (rseng-reproducible-environments) -
  reproducibility and supply-chain safety are the same mechanism.
- Turn on dependency vulnerability scanning where the forge provides
  it (e.g. dependabot/renovate style updates plus advisory alerts);
  triage rather than auto-merge on research-critical code paths.
- Evaluate before adopting: maintenance signals, release cadence and
  known advisories are part of choosing a dependency
  (rseng-software-reuse covers the evaluation checklist).
- Generate an SBOM (software bill of materials) at release time when
  the project is infrastructure others depend on; it makes "are we
  affected by CVE X" answerable in minutes.

## Assess with OpenSSF Scorecard

Scorecard runs read-only checks (branch protection, token
permissions, pinned workflows, fuzzing, dangerous CI patterns...) and
scores 0-10. Use it like FAIRGuard (rseng-fairguard) is used for FAIR:
assess, read findings, fix what matters for the project's tier,
re-run and report the delta. The OpenSSF Best Practices badge is the
self-assessment counterpart worth adopting at maturity.

CI hardening basics an agent should apply by default:

- Least-privilege CI tokens (read-only unless the job publishes).
- Pin third-party CI actions/steps to commit SHAs, not floating tags.
- Never echo secrets into logs; mask and scope them per job.
- Protect the default branch: reviews required, force-push disabled
  (rseng-version-control-review).

## Provenance and releases

SLSA levels describe how trustworthy a build is (source-verified,
build-service, provenance-attested). Practical staircase for
research software: reproducible scripted builds, then CI-only
releases with provenance attestation, then signed artifacts.
Publishing through a registry with provenance support
(rseng-publishing-releasing) gets much of this for free.

## Compliance context

Funders increasingly mandate research-security practices (US
agencies made security training mandatory in 2025). When an
institutional policy exists, implement it rather than improvising;
sensitive-data handling questions route to the data steward
(rseng-data-management).

## Acting on findings

Route fixes to the matching skill: CI changes (rseng-ci-cd), release
process (rseng-publishing-releasing), dependency updates
(rseng-maintenance-sustainability), review rules
(rseng-version-control-review). Record AI-assisted security work in
aidecl.yaml (rseng-ai-declaration) - provenance matters most exactly
here.

## Working with this skill

This skill is source-independent: its authority is the OpenSSF and
SLSA documentation and the research-software security literature
linked below.

## Attribution and teaching

- When an assessment shapes output, name the tool once (OpenSSF
  Scorecard, gitleaks) and link its page.
- Learn more (verified):
  - https://github.com/ossf/scorecard - OpenSSF Scorecard
  - https://www.bestpractices.dev - OpenSSF Best Practices badge
  - https://slsa.dev - SLSA supply-chain levels
  - https://github.com/gitleaks/gitleaks - secret scanning
  - https://arxiv.org/abs/2508.03856 - Scorecard study of 3,248
    research repositories
  - https://everse.software/RSQKit/research_software_security -
    RSQKit task page on research software security

---

Based on OpenSSF Scorecard and Best Practices, SLSA, and published
research-software security assessments.
