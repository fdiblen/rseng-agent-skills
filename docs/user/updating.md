# Updating and troubleshooting

This page covers how to move an install to a newer version of the pack, how
to read what the tools tell you, and what to do when something looks wrong.

The CLI (`npx rseng-agent-skills`) manages installs for Copilot, Cursor, Codex
CLI, Gemini CLI, and the standard-layout Claude skill files. Claude Code
used as a plugin updates through its own marketplace instead - see
[Claude Code plugin updates](#claude-code-plugin-updates) below.

## Updating a CLI install

```
npx rseng-agent-skills update
```

With no agent named, this updates every existing install the CLI finds - an
install being any target that has a manifest (`.rseng-agent-skills.json`) written
by a previous install. If no install has a manifest, the command stops with:

```
no existing installs found (no manifest); run install
```

Restrict the update to specific agents by naming them:

```
npx rseng-agent-skills update copilot cursor
```

`install` differs from `update` here, deliberately: `install` restores the
pack's own copy of a file even when you have edited it, saving your version
into a backup first and saying so. That is how you get back to a clean copy.
Use `update` when you want your edits kept in place. A backup holding files
that were yours carries a `.rseng-your-files` marker and is never pruned.

### What update actually does

The update is deliberately conservative. It never blindly overwrites your
files:

- Managed files - files whose current content still matches the hash the
  manifest recorded at install time - are replaced with the new version.
- User-edited files - files whose content no longer matches the recorded
  hash, meaning you changed them - are preserved and reported by name. Your
  edits win.
- Files the new release no longer ships are removed, but only when their
  content still matches what was installed. Anything you edited is left
  alone, and a file another installed agent still claims is left alone too.
  Removals are printed by name.
- Before anything is written, the previous state of every file that will
  actually change is copied into a fresh backup directory inside the install
  directory, named with an `.rseng-backup-` prefix. An update that changes
  nothing creates no backup. On success the command prints the location:

```
claude: preserved user-edited files: rseng-testing/SKILL.md
claude: backup at /path/to/.claude/skills/.rseng-backup-a1b2c3
```

A preserved file keeps its original recorded hash in the manifest, so it
stays recognised as user-edited and stays protected on every future update -
you will not silently lose an edit two updates later.

Backups do not pile up: after a successful update the three most recent are
kept and older ones are removed, and the command says how many it cleared.
Each backup is a full copy of every managed file, so without that cap they
would grow inside your project unnoticed. If you want to keep one for
longer, move it somewhere outside the install directory.

### Preview an update without touching anything

Use the global `--dry-run` flag to see what would change:

```
npx rseng-agent-skills update --dry-run
```

This reports the plan and writes nothing - no files replaced, no backup
directory created. The output names how many managed files would be updated
and which user-edited files would be preserved:

```
[dry-run] claude: would update 12 managed files, preserving 1 user-edited: rseng-testing/SKILL.md
```

`--dry-run` works with `install` as well, so you can preview a first install
the same way.

## Checking install health with doctor

```
npx rseng-agent-skills doctor
```

`doctor` inspects every agent target it knows about and changes nothing. It
prints one line per target. A target with no manifest reports:

```
claude (project): not installed
```

An installed target reports its version, whether it is current, and a file
tally:

```
claude (project): v0.1.0, up to date, 18 intact
```

Read each part as follows:

- `v0.1.0` - the version recorded in the manifest at install time.
- `up to date` or `STALE (pack is vX)` - STALE means the installed version
  differs from the pack version now available; run `update` to refresh it.
  "up to date" means the two match.
- `N intact` - files whose content still matches the recorded hash. These
  are cleanly managed and will be updated normally.
- `M user-edited (files)` - files you have changed since install; listed by
  name. These are protected and will be preserved on update.
- `K MISSING (files)` - files the manifest expects but that are no longer on
  disk; listed by name. Run `update` (or `install`) to restore them.

A fuller line combining the states looks like this:

```
claude (project): v0.1.0, STALE (pack is v0.2.0), 16 intact, 1 user-edited (rseng-testing/SKILL.md), 1 MISSING (rseng-licensing/SKILL.md)
```

## Claude Code plugin updates

If you installed rseng-agent-skills as a Claude Code plugin (via
`/plugin marketplace add` and `/plugin install`), the CLI's `update` and
`doctor` commands do not manage it - the plugin system does. Update it
through the marketplace:

```
/plugin marketplace update fdiblen/rseng-agent-skills
/plugin update rseng-agent-skills
```

The CLI is only for the standard skill-file installs (`.claude/skills/` and
the other agents). Use whichever mechanism you installed with; do not mix
the two for the same target.

## Troubleshooting FAQ

### A skill is not triggering

Skills trigger on the wording of your request matching the skill's "Use
when the user asks..." triggers, not on an explicit call. If nothing fires:

- Make the request more specific to the task the skill covers - name the
  artifact or tool (for example "write a CITATION.cff", "set up pytest",
  "add a Dockerfile") rather than asking abstractly.
- Confirm the install is present and healthy with `npx rseng-agent-skills
  doctor`. A `MISSING` file or `not installed` line explains a skill that
  cannot fire.
- For Claude Code, remember the `/rseng-*` slash commands and the
  subagents are explicit entry points you can always invoke by name when
  you do not want to rely on automatic triggering.

### How do I see what an update would change first

Run it with `--dry-run` (see above). It reports the count of managed files
that would be updated and names the user-edited files that would be
preserved, without writing anything or creating a backup.

### How do I restore a file from a backup

Every real (non-dry-run) update copies the prior state of its managed files
into an `.rseng-backup-` directory inside the install directory, and prints
the path. To undo an update, copy the file you want back from that directory
to its original location. The backups mirror the relative paths of the
managed files, so a skill at `rseng-testing/SKILL.md` sits at the same
relative path under the backup directory.

### I edited a file and the update skipped it - is that a bug

No. That is the preservation behaviour working as designed. Once a managed
file no longer matches its recorded hash, `update` treats it as
user-edited, keeps your version, and reports it by name. If you instead want
the fresh pack version, move or delete your edited copy and run `update`
again (the file will then be restored as a managed file), or restore it
from the pack with a fresh `install`.

### Where should I report a problem

Both content and packaging problems belong to this project - a factual
error or outdated recommendation in a skill body, as much as a skill not
installing, a broken CLI command, wrong file placement for an agent, or
incorrect `doctor` output. Report either on the rseng-agent-skills issue tracker
at [https://github.com/fdiblen/rseng-agent-skills](https://github.com/fdiblen/rseng-agent-skills).
If a "Learn more" link points at material that is itself wrong or stale,
that belongs to the linked project; report the link choice here.
