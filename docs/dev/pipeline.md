# Content pipeline

The pipeline lives in `pipeline/src/rseng_pipeline/`. It turns the pinned
RSQKit sources named in `extensions/rsqkit/upstream.lock` into two build artifacts
(`build/<source>/content.json` and `build/fragments/*.md`) and then two sets of
consumers: the generated `references/` folders inside each skill and the
per-agent adapter outputs in `dist/`. This page documents each module - its
job, its inputs and outputs - and the commands to run each stage.

All commands assume [uv](https://docs.astral.sh/uv/). The pipeline is a uv
project rooted at `pipeline/`, so run modules with
`uv run --directory pipeline python -m rseng_pipeline.<module>`. The
`justfile` at the repo root wraps the common tasks (`just test`,
`just lint`, `just fix`, `just hooks`).

## Stage order

```
fetcher -> parser -> cleaner -> url_verify -> learn_more -> assembler
                                                              |
                                          +-------------------+
                                          v                   v
                                     references         adapters/build_adapters
```

`registry` and `checks` are helpers used within those stages rather than
stages of their own. Four entry points chain together: `fetcher` downloads
the pinned sources into the cache (run it first on a fresh checkout -
`assembler` verifies the cache but never fetches), `assembler` runs parse
through learn-more and writes the build artifacts, and `references` and
`build_adapters` read those artifacts:

```
uv run --directory pipeline python -m rseng_pipeline.fetcher
uv run --directory pipeline python -m rseng_pipeline.assembler
uv run --directory pipeline python -m rseng_pipeline.references
uv run --directory pipeline python -m rseng_pipeline.build_adapters
```

## fetcher.py

Downloads the pinned upstream files into `pipeline/cache/<source>/` and records a
manifest so later runs can verify integrity instead of re-downloading.

- `load_pin(lock_path)` reads `upstream.lock` into an `UpstreamPin`
  (repo, ref, commit, source `paths`, `data_globs`).
- `selects(pin, path)` decides whether a repository path is in scope. It
  skips `TEMPLATE_*` files and anything that is not `.md`/`.yml`/`.yaml`,
  then matches the pin's `paths` prefixes and `data_globs` (a directory-
  aware glob where `*` does not cross `/`).
- `list_upstream_files(pin)` enumerates matching blobs from the pinned
  commit's git tree via the GitHub trees API.
- `fetch(pin, cache_dir, files=None, force=False)` downloads each selected
  file from `raw.githubusercontent.com` at the pinned commit, skipping
  files already cached with a matching hash for that commit unless
  `force=True`, and writes `cache/manifest.json` (repo, commit, per-file
  SHA-256).
- `verify_cache(cache_dir)` returns a list of problems (missing manifest,
  missing file, hash mismatch); an empty list means the cache is intact.

Inputs: `upstream.lock`, network. Outputs: files under `cache/` plus
`cache/manifest.json`.

## parser.py

Parses each cached markdown page into a normalized `PageRecord`, smoothing
out upstream frontmatter irregularities so downstream stages never touch
raw frontmatter.

- `parse_page(text, source_path)` / `parse_page_file(path, root)` build a
  `PageRecord` (page_id, title, description, keywords, contributors,
  related_pages, quality_indicators, child_pages, body, source_path,
  extra). It normalizes the two frontmatter quirks: hub pages use
  `indicators` instead of `quality_indicators` (both are merged and
  deduped), and `related_pages` may be a list or a mapping (a bare list
  becomes `{"tasks": [...]}`). When a page has no `page_id`, the filename
  stem is used instead.
- `load_pages(cache_dir)` parses every `cache/pages/**/*.md` file into a
  dict keyed by `page_id`. Because the key is the frontmatter `page_id`,
  filenames that differ from their `page_id` are handled transparently
  (see [Taxonomy](taxonomy.md) for the three known mismatches).
- `build_section_tree(body)` builds a nested heading tree, ignoring
  headings inside fenced code blocks; `iter_sections` walks it depth-first.
- `extract_tool_refs(body)` returns the tool-registry ids referenced by
  `{% tool "..." %}` tags, in order.

Inputs: cached pages. Outputs: in-memory `PageRecord` objects (persisted
later by the assembler).

## registry.py and sources/rsqkit.py

Loads the RSQKit `_data/*.yml` registry files into typed lookups.

- `load_tools(path)` -> `dict[id, Tool]` (id, name, description, url,
  catalog).
- `load_contributors(path)` -> `dict[name, Contributor]`.
- `load_dimensions(path)` -> `dict[abbr, Dimension]` from the rsqd
  JSON-LD registry.
- `load_indicators(path)` -> `dict[abbr, Indicator]` from the rsqi
  registry, resolving each indicator's quality-dimension `@id` references
  to dimension abbreviations.

Descriptions are whitespace-collapsed; IRI tails are stripped of stray
whitespace but genuine content errors are left visible for validation.

## cleaner.py

Turns a raw RSQKit page body into portable markdown that works outside the
upstream Jekyll site. Fenced code blocks are passed through untouched.

- `replace_tool_tags(body, tools)` turns `{% tool "x" %}` into a markdown
  link (or plain name) using the tool registry.
- `strip_liquid(body)` removes remaining Liquid tags/variables and drops
  lines they leave empty.
- `drop_empty_training_sections(body)` removes Training headings whose
  section has no real content (upstream Training blocks are mostly dynamic
  embeds), keeping genuinely curated ones.
- `resolve_internal_links(body)` rewrites site-relative links to absolute
  `https://everse.software/RSQKit/` URLs so fragments keep working when
  embedded elsewhere.
- `clean_body(body, tools=None)` runs all of the above, strips trailing
  whitespace line by line, and collapses blank runs - producing byte-stable
  output under standard whitespace hooks.

## url_verify.py

Verifies external URLs before they reach generated content. The probe
function is injectable so tests and offline runs work without network.

- `load_quarantine(path)` reads `data/url_quarantine.yml` into a
  `{url: reason}` map of human-flagged URLs.
- `probe_url(url, timeout)` issues an HTTP HEAD, retrying once with GET on
  403/405/501 (CDNs that reject HEAD).
- `verify_url(url, quarantine, probe)` returns a `URLCheck` with status
  `ok` / `quarantined` / `broken` / `error`. Quarantined URLs are rejected
  without probing.
- `verify_urls(urls, ...)` verifies each distinct URL once, keyed by URL.

## learn_more.py

Collects the per-page "Learn more" pointers, verifies them, and merges in
curated sources.

- `collect_learn_more(record)` / `collect_all(pages)` extract each page's
  own RSQKit deep link plus the external links in its cleaned body, with
  links inside Training sections tracked separately. Tool homepages are
  deliberately excluded - they reach skills through the tool registry.
- `load_curated(path)` reads `data/curated_learn_more.yml` into pack-wide
  `defaults` plus per-page additions; `merge_curated(...)` attaches curated
  sources to every page's entry.
- `verify_learn_more(entries, quarantine, probe)` verifies every distinct
  URL once (via `url_verify`) and drops any that are not `ok`, returning the
  filtered entries plus the full check results so callers can report what
  was rejected.

## assembler.py

The main entry point. Reads the verified cache plus the data files and emits
the build artifacts.

- `assemble(pipeline_dir, build_dir=None, pin=None)` verifies the cache
  (raising if not intact), loads pages and the four registries, builds and
  merges learn-more entries, then writes:
  - `build/fragments/<page_id>.md` - the cleaned markdown for each page,
    each with a generated-file header carrying source path, upstream
    commit, and license/DOI.
  - `build/<source>/content.json` - every page entry (title, description, keywords,
    contributors, related pages, quality indicators, child pages,
    `source_path`, `rsqkit_url`, `tool_refs`, and the `learn_more` lists),
    plus the tools, contributors, dimensions, and indicators registries,
    plus the upstream provenance block. The cleaned page body is not stored
    in `content.json`; it lives only in the fragment files.

Run it:

```
uv run --directory pipeline python -m rseng_pipeline.assembler
```

This assumes the cache is already populated (the assembler verifies but
does not fetch).

## references.py

Generates each skill's `references/` folder from the build artifacts,
driven by `extensions/rsqkit/taxonomy.yml`.

- `load_taxonomy(path)` returns the `skills:` mapping; `skill_page_ids`
  concatenates a skill's `pages`, `concept_pages`, and `role_pages`.
- `generate_references(skills_dir, taxonomy_path, build_dir)` for each skill
  wipes and rebuilds `references/` (so removed upstream pages prune
  automatically) and writes:
  - a references.md section per source - source-page links plus
    mapped page. A missing fragment for a mapped `page_id` raises
    `FileNotFoundError`, which is how a taxonomy/upstream mismatch surfaces.
  - `references/tools.md` - the registry tools referenced by those pages.
  - `references.md` - curated training plus verified external
    pointers, deduped.
  - `references.md` - a quality-indicator checklist grouped by
    dimension (the router skill, which maps no task pages, gets the full
    registry).

Run it:

```
uv run --directory pipeline python -m rseng_pipeline.references
```

## adapters.py

The adapter build framework (not a runnable stage on its own).

- `load_render_context(repo_root)` builds one context dict shared by every
  template: the generated note, upstream provenance, the citation snippet
  (from `data/citation.yml`), the skill entries (name, description, scope,
  mapped pages - pulling titles/URLs from `content.json` and descriptions
  from each `SKILL.md` frontmatter), and the plugin command entries (from
  `commands/*.md`).
- `template_env(repo_root)` returns a jinja2 `Environment` over
  `adapters/templates/` with `StrictUndefined` (so a missing variable is a
  hard error).
- `copy_skills(repo_root, target_dir)` copies the canonical `rseng-*`
  skill folders through verbatim (used by several targets).
- `render_to(...)` renders one template to one output path.
- `TARGETS` plus the `@target(name)` decorator form the registry that
  concrete targets register into. The target modules live in
  `targets/` (`copilot`, `cursor`, `codex`, `gemini`); importing the
  package registers them all.

## build_adapters.py

Builds every registered adapter target into `dist/`.

- `build(repo_root, only=None)` loads the render context and template
  environment, then for each target wipes and recreates `dist/<target>/`,
  calls the target's build function, and runs `check_target` on the result.
  Any check problem aborts the build with `SystemExit`.

Run it (all targets, or a subset):

```
uv run --directory pipeline python -m rseng_pipeline.build_adapters
uv run --directory pipeline python -m rseng_pipeline.build_adapters copilot gemini
```

The per-target modules define the output layout: Copilot writes
`.github/copilot-instructions.md` plus one `instructions/*.instructions.md`
per skill and a `skills/` passthrough; Cursor writes `.cursor/rules/*.mdc`
(one overview rule plus one per skill); Codex writes a size-checked
`AGENTS.md` plus a `skills/` passthrough; Gemini writes an extension
manifest, `GEMINI.md`, TOML commands translated from the Claude command
bodies, and a `skills/` passthrough.

## checks.py

Post-render validation run by `build_adapters` after each target renders; a
non-empty problem list fails the build. Checks are format-driven:

- Character/byte budgets for whole-file context docs
  (`copilot-instructions.md` 12 KiB, `GEMINI.md` 24 KiB, `AGENTS.md`
  32 KiB).
- Required frontmatter fields for `.instructions.md`
  (`description`, `applyTo`) and `.mdc` (`description`, `alwaysApply`).
- TOML validity plus required `description`/`prompt` for Gemini commands;
  JSON validity for `.json` files.
- Residue checks: a leaked `CLAUDE_PLUGIN_ROOT` placeholder, or unrendered
  template/Liquid `{%` markers in `.md`/`.mdc` files.

Canonical passthrough content (`references/` files and `SKILL.md`) is
skipped here - it is validated at its source, not per adapter.

## Data files

Under `extensions/rsqkit/data/` (hand-maintained inputs, not generated):

- `citation.yml` - the shared citation snippet (`full`, `short`,
  `markdown`); the single source of truth for attribution wording across
  every target.
- `url_quarantine.yml` - URLs a human flagged as non-canonical; rejected by
  `url_verify` without probing.
- `curated_learn_more.yml` - curated training/reference sources merged into
  the per-page learn-more lists (pack-wide `defaults` plus per-page
  additions); every URL is verified by the pipeline.
- `dimensions_note.yml` - a resolution note recording that the pinned
  upstream defines 13 quality dimensions, for skill authors.

## Tests

Tests live in `pipeline/tests/` (`test_fetcher.py`, `test_parser.py`,
`test_cleaner.py`, `test_registry.py`) with verbatim upstream fixtures under
`tests/fixtures/` (excluded from whitespace hooks to keep their bytes
intact). Run them with:

```
```

or `just test` from the repo root. Lint and format with `just lint` /
`just fix` (ruff), and install the pre-commit hooks with `just hooks`.
