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

## Publishing credentials

The publish workflow authenticates to the registry with an `NPM_TOKEN`
repository secret. Without it the run still builds and tests everything,
then fails at the publish step with `ENEEDAUTH`, so the workflow checks
for the secret up front and stops immediately if it is missing.

Create the token on npmjs.com under Access Tokens - granular tokens
cannot be made from the CLI - with read and write permission and the
shortest expiry that covers the release, then:

```
gh secret set NPM_TOKEN --repo fdiblen/rseng-agent-skills
```

A granular token can normally be restricted to this package alone. That
is not possible for the very first publish: the package picker only
lists packages that already exist, so the bootstrap token has to cover
all packages. Give it a short expiry and revoke it once the package is
on the registry.

### Moving to trusted publishing

Once the package exists, the token can be replaced with OIDC, which
needs no stored credential at all:

```
npm trust github rseng-agent-skills --file publish.yml \
  --repo fdiblen/rseng-agent-skills --allow-publish
```

The command needs npm 11.10.0 or later and prompts for a second factor,
so it is run from a terminal rather than from CI. Trusted publishing
cannot bootstrap a package that has never been published, which is why
the first release goes out on a token.

After it is configured, drop `NODE_AUTH_TOKEN` and the credential check
from `publish.yml` and delete the secret. The `--provenance` flag also
becomes unnecessary, because attestations are generated automatically
when a publish is authenticated through OIDC.

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

- checks the registry credential is present, and that the tag matches the
  version in `installer/package.json` - a mismatch would otherwise publish
  whatever the package file says under an unrelated tag;
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

## What the release notes cover

Release notes summarize what changed per skill - added skills, updated
bodies, removed or renamed skills - plus any installer or adapter
changes that affect what lands on a user's machine. Since every derived
artifact regenerates from the tagged commit, the tag itself is the full
provenance of a release.
