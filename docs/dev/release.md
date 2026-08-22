# Release

Releasing cuts a versioned build and publishes it. Everything a release
ships is reproducible from the repository - the generated artifacts are
rebuilt from the skills on a clean checkout, nothing generated is
hand-maintained.

## Cut a release

1. Bump the version in `installer/package.json` (`"version"`). The installed
   manifest also carries a version, and the plugin manifests
   (`.claude-plugin/plugin.json`) have their own - keep them consistent for a
   release; `CITATION.cff`, `codemeta.json` and the changelog entry carry it
   too.
2. Move the `Unreleased` items in `CHANGELOG.md` under a new version
   heading with the date, and refresh the compare links at the bottom.
3. Tag the commit `v<version>` (for example `v0.1.0`) and push the tag.
4. Publishing the GitHub release object triggers the artifact attach.

## Release notes

The GitHub release body is written from the changelog entry, expanded
with a per-skill summary: list skills added, skills with substantive
body updates, and skills removed or renamed since the previous tag
(`git diff --stat v<prev>..v<new> -- skills/` locates them). Keep the
npm side automatic - the package README ships as-is; only the GitHub
release carries the narrative notes.

## Archive the release

- Zenodo: the repository carries `.zenodo.json` (kept consistent with
  `CITATION.cff` and `codemeta.json` - same title, description shape,
  creators, license, keywords). With the GitHub-Zenodo integration
  enabled for the repository, publishing the GitHub release deposits
  the archive and mints the version DOI automatically; copy the DOI
  badge into the README and add the DOI to `CITATION.cff` afterwards.
- Software Heritage: after the release is public, submit the
  repository at https://archive.softwareheritage.org/save/ (save code
  now, origin type git, the repository URL) - or POST to
  `https://archive.softwareheritage.org/api/1/origin/save/git/url/<repo-url>/`.
  No account is needed; the save request is idempotent, so repeat it
  at every release.

## What the workflows do

`.github/workflows/publish.yml` runs on any `v*` tag push. It:

- builds the adapters from scratch on a clean checkout, in the order the
  pipeline expects - `references` (regenerate every skill's
  `references.md`), then `build_adapters` (render `dist/<target>/` and
  run the output checks);
- builds and tests the installer (`npm ci`, `npm run build`, `npm test`);
- publishes the npm package with provenance (`npm publish --provenance --access public`).

Because the release rebuilds everything from the skills on a clean
machine, a tag can only publish content that regenerates cleanly - a
failing check stops the release before publish.

`.github/workflows/release-artifacts.yml` runs when a GitHub release is
*published*. It rebuilds the adapters the same way, zips each `dist/<target>/`
into `rseng-agent-skills-<target>.zip`, and uploads the zips to the release with
`gh release upload`. So the npm package (installer) and the per-agent zips
(for manual installation) come from two separate triggers: the tag push
publishes to npm, and publishing the release object attaches the zips.

## Semver policy

The version number encodes the kind of change:

- **patch** - regeneration only: regenerated references, directory blocks
  or adapter outputs, typo fixes, with no change to hand-authored skill
  bodies.
- **minor** - body updates or new skills: substantive guidance changes in a
  skill body, or an added skill.
- **major** - restructuring: skills removed or renamed in a way that
  reshapes the skill set, or frontmatter schema changes.

Skill names are stable identifiers, so adding a skill does not break an
existing install - which is why new skills are a minor, not a major, bump.

## Release notes

Release notes summarize what changed per skill - added skills, updated
bodies, removed or renamed skills - plus any installer or adapter
changes that affect what lands on a user's machine. Since every derived
artifact regenerates from the tagged commit, the tag itself is the full
provenance of a release.
