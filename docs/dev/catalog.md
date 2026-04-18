# External skills catalog

catalog.yml at the repository root makes including third-party skills,
extensions and add-ons easy without making it dangerous: developers
propose ONLINE LINKS (github repositories, websites, marketplaces,
registries), the links live in a categorized catalog, and content only
enters the collection after a human review.

## Lifecycle

1. Propose - add an entry with name, url, kind (github, website,
   marketplace, registry), category and status: proposed. No content is
   fetched; CI only validates the entry's shape.
2. Review - a maintainer pins a commit (`pin:` full sha for github
   entries) and runs

       uv run --directory pipeline python -m rseng_pipeline.catalog stage <name>

   which downloads that exact commit into the git-ignored staging/ area
   and writes a review report: files extracted, SKILL.md folders found,
   and any executable or binary files flagged for careful inspection.
   Nothing outside staging/ is touched.
3. Include - after review, copy the accepted skill folders into skills/,
   set the entry's status to included, list the vendored `skills:` and
   record the `review:` block (by, date). From then on the build treats
   them like any other skill: adapters, installer bundling and the
   Claude plugin all discover every skills/*/SKILL.md folder.

## Why not fetch during the build

Skills are prompt content: pulling them from the network at build time
would let an upstream change walk straight into every user's agent - a
supply-chain risk. The catalog therefore separates POINTING at content
(cheap, unreviewed) from SHIPPING it (pinned, staged, human-reviewed,
vendored). `python -m rseng_pipeline.catalog check` runs in CI and fails
when an included entry is malformed or its vendored skills are missing;
it never touches the network.

## Sources vs catalog

Content-source extensions (extensions/) feed reference material INTO
existing skills through a pinned pipeline; the catalog brings in WHOLE
third-party skills. A catalog entry that turns out to deserve deep
integration can graduate into an extension later.
