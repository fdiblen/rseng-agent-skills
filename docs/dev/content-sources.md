# Content sources

The engine in pipeline/ is source-agnostic: everything specific to one
body of upstream content lives in a content-source extension under
extensions/<name>/. The bundled sources are rsqkit (RSQKit) and nlesc-guide (the eScience Center guide).

## What an extension provides

- source.yml - name, human title, site and base URL (used to resolve
  relative links in cleaned pages), DOI and content license (used for
  attribution in generated fragments)
- upstream.lock - the pinned upstream repository and commit plus the
  source path selectors
- upstream.manifest.json - per-file SHA-256 hashes at the pin, written by
  `python -m rseng_pipeline.lock_manifest` and consumed by the sync
  classifier
- taxonomy.yml - the mapping of upstream page ids to skills; the contract
  that drives references.md generation and per-skill sync impact
- data/ - citation strings (citation.yml), the URL quarantine list,
  curated learn-more sources, and any source-specific data notes
- a loader module in pipeline/src/rseng_pipeline/sources/<name>.py when the
  source ships registry-like data in its own format (rsqkit parses the
  EVERSE JSON-LD tool/indicator/dimension registries)

## How the engine uses it

`rseng_pipeline.extension.extension_dir()` locates the extension and
`rseng_pipeline.source.load_source()` reads source.yml. The fetcher,
assembler, references generator, adapter builder, link checker and sync
classifier all take their source-specific inputs from there; nothing
else in the engine names a concrete source.

## Adding a second source

Create extensions/<name>/ with the files above, map its pages into
skills via its taxonomy.yml, and add a loader module if it has registry
data. The engine iterates every installed extension: each gets its own
cache namespace (pipeline/cache/<name>/), its own build output
(pipeline/build/<name>/) and its own section in the references.md of
every skill it maps pages to. The sync classifier reports per
source. An extension may also contribute entirely new skills by mapping
pages to skill names that do not exist yet - author the SKILL.md for
them the same way as the core set.
