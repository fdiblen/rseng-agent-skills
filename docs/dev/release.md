# Release

Releasing cuts a versioned build and publishes it. Everything a release
ships is reproducible from the repository - the generated artifacts are
rebuilt from the skills on a clean checkout, nothing generated is
hand-maintained.

## Cut a release

1. Bump the version in `installer/package.json` (`"version"`). The installed
   manifest also carries a version, and the plugin manifests
   (`.claude-plugin/plugin.json`) have their own - keep them consistent for a
   release.
2. Tag the commit `v<version>` (for example `v0.1.0`) and push the tag.
3. Publishing the GitHub release object triggers the artifact attach.

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
