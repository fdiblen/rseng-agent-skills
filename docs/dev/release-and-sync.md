# Release and sync

Two related processes keep the pack current: **releasing** cuts a versioned
build and publishes it, and **syncing** pulls new content-source updates in and
classifies their impact. Both hang off the pinned sources of truth in
`extensions/<source>/upstream.lock` (one per content source), and both are
reproducible from them - nothing generated is hand-maintained.

## Releasing

### Cut a release

1. Bump the version in `installer/package.json` (`"version"`). The installed
   manifest also carries a version, and the plugin manifests
   (`.claude-plugin/plugin.json`) have their own - keep them consistent for a
   release.
2. Tag the commit `v<version>` (for example `v0.1.0`) and push the tag.
3. Publishing the GitHub release object triggers the artifact attach.

### What the workflows do

`.github/workflows/publish.yml` runs on any `v*` tag push. It:

- builds the adapters from scratch on a clean checkout, in the same order the
  pipeline expects -
  `assembler` (fetch/verified cache to `content.json` + fragments), then
  `references` (regenerate every skill's `references.md`), then `build_adapters`
  (render `dist/<target>/` and run the output checks);
- builds and tests the installer (`npm ci`, `npm run build`, `npm test`);
- publishes the npm package with provenance (`npm publish --provenance --access public`).

Because the release rebuilds everything from the lock on a clean machine, a
tag can only publish content that regenerates cleanly - a broken taxonomy or a
failing check stops the release before publish.

`.github/workflows/release-artifacts.yml` runs when a GitHub release is
*published*. It rebuilds the adapters the same way, zips each `dist/<target>/`
into `rseng-agent-skills-<target>.zip`, and uploads the zips to the release with
`gh release upload`. So the npm package (installer) and the per-agent zips
(for manual installation) come from two separate triggers: the tag push
publishes to npm, and publishing the release object attaches the zips.

### Semver policy

The version number encodes the kind of change, driven by the sync
classification below:

- **patch** - regeneration only: upstream body text, tool descriptions and
  typo fixes flow through without any change to hand-authored bodies or the
  taxonomy.
- **minor** - body updates or new skills: substantive guidance changes in a
  skill body, or an added skill.
- **major** - taxonomy restructuring: page_ids added, removed or renamed in a
  way that reshapes the skill set, or frontmatter/registry schema changes.

Skill names are stable identifiers, so adding a skill does not break an
existing install - which is why new skills are a minor, not a major, bump.

### Release notes

Release notes **must state the upstream source commits** the build was cut from -
the `commit` in each `extensions/<source>/upstream.lock`. Every generated artifact already
stamps that SHA (fragment headers, the `upstream` block in `content.json`, the
generated-note banners), so the notes and the artifacts always agree on
provenance. Release notes also carry a change summary generated from the sync
impact reports rather than hand-kept, so the CHANGELOG section is a build
product, not a manually edited file.

## Syncing with upstream

### The pins

Each content source has its own pin: `extensions/<source>/upstream.lock`
records that source's upstream repo, the `ref` it tracks (`main`) and the
exact `commit` the current build is pinned to, plus the source paths and
data globs the pipeline consumes. The rsqkit pin, for example:

```toml
[upstream]
repo = "https://github.com/EVERSE-ResearchSoftware/RSQKit"
ref = "main"
commit = "03a8352e0701acf6ae28a1f6c9069e9b2caf8e7e"
```

The fetcher downloads exactly the selected files at that commit and records a
SHA-256 manifest, so later runs verify cache integrity instead of
re-downloading (`fetcher.py`, `verify_cache`). The locks are machine-updated
by the sync workflow; the comment in each file asks contributors not to edit
the commit by hand. Advancing a pin is what a sync *is*.

### The weekly sync classifier

The sync workflow (`.github/workflows/sync.yml`) runs on a weekly cron
(plus manual dispatch). It diffs each pinned lock against the source's
upstream `main`, regenerates, and opens a single PR carrying a per-skill
impact report. Because each source's `taxonomy.yml` maps page_ids to
skills, change detection is per-skill and per-source rather than
all-or-nothing: each changed upstream page is attributed to the skill(s)
that map it.

The classifier sorts every change into one of three levels:

- **L1 references-only** - upstream body text, tool descriptions, typo fixes.
  These touch only generated `references.md`, so regeneration is safe; the
  sync PR is labelled L1 and auto-merges once CI is green.
- **L2 body-review** - substantive guidance changes in a page that backs a
  hand-authored SKILL.md body. The PR flags each affected skill with the
  upstream diff excerpt and a review checklist, and a human reviews whether the
  body needs updating. An AI-drafted body update may be attached as a separate,
  human-reviewed commit.
- **L3 structural** - new, deleted or renamed page_ids, or frontmatter/registry
  schema changes. Drift tests fail CI until a human updates `taxonomy.yml`; the
  pin does not advance silently past a structural change.

Registry changes (tools, indicators, dimensions) are diffed separately, with
URL re-verification for new or changed tool links.

### Page additions and removals

The setup expects the content sources to grow and shrink:

- **New page** - shows up as L3 until it is mapped. The sync PR proposes a
  `taxonomy.yml` mapping to an existing skill (matched on keywords and
  `related_pages`) or proposes a new skill when nothing fits; a human confirms
  the mapping, after which `references.md` and the adapters regenerate
  automatically.
- **Removed page** - generated `references.md` prunes automatically (the
  reference build rewrites every file in full, so a page that is gone disappears);
  any skill whose body cites the removed page_id is flagged for review. A skill
  whose backing pages all disappear is deprecated for one minor release with a
  note, then removed.
- **Renamed page_id** - treated as remove plus add, with the classifier
  hinting at the rename when content similarity is high.

Simulation fixtures (an added page, a removed page, a renamed page_id) keep the
classifier output, reference pruning, drift-test failures and triage
suggestions under continuous test rather than only exercised when upstream
actually moves.

### Why generated output stays uncommitted at build but pruned on sync

The reference generator and the adapter builder both rewrite their output
from scratch on every run, so removals propagate without manual cleanup.
That is the same property the sync relies on: advancing a pin and
rerunning the pipeline is sufficient to bring every derived artifact - the
`references.md` files, `dist/`, the release zips - back in line with upstream.

## Triage procedure for sync PRs

The weekly sync workflow labels each PR with its level; handle them as
follows.

L1 (references-only): nothing to do. The PR has auto-merge enabled and
lands once the validate workflow is green. Spot-check the diff if the
registry changes look unusually large.

L2 (body review): open the change report in the PR body. For every skill
it lists, read the upstream diff of the underlying page and decide
whether the hand-authored SKILL.md body still summarizes it faithfully.
Update the body in the same PR when it does not. Merge manually. An
optional helper, `.github/workflows/sync-draft.yml`, can draft the body
updates for you: a maintainer dispatches it on the sync branch, it
compares each L2 skill's body against the updated fragments and commits
draft revisions to the PR, which still go through normal human review.
It never runs automatically and needs the ANTHROPIC_API_KEY secret.

L3 (structural): the PR needs taxonomy work before it can merge.

1. Added pages: the report suggests a target skill (keyword and
   related_pages matching) or proposes a new skill. Confirm or correct
   the suggestion in the source's extensions/<source>/taxonomy.yml,
   regenerate references, and
   check the new page's indicators appear in the skill checklist.
2. Removed pages: references have pruned automatically; the report lists
   every skill whose body cites the removed page_id - edit those bodies.
   If a skill has lost all of its pages, deprecate it (keep it one minor
   release with a deprecation note in the description, then delete).
3. Renamed page_ids: update the id in taxonomy.yml, then treat as a
   removed-plus-added pair for body review. The classifier hints at
   renames when a removed and an added page share keywords.

After any L3 edit, run the drift tests locally
until the taxonomy and the cache agree again.
