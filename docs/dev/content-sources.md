# Content sources

The engine in pipeline/ is source-agnostic: everything specific to one
body of upstream content lives in a content-source extension under
extensions/<name>/. The bundled source is rsqkit.

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
  that drives references/ generation and per-skill sync impact
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
data. Multi-source builds are not wired end to end yet - the engine
currently builds the default source - so treat a second source as an
engine contribution, not just a data drop; the seams listed above are
where the work goes.
