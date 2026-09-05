import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import type { AgentTarget } from "./agents.js";
import type { CliContext } from "./context.js";

/**
 * Per-agent manifest: the unified targets (codex, cursor, copilot) all
 * install into the project root, so each agent's record needs its own
 * file name to coexist.
 */
export function manifestName(agent: string): string {
  return `.rseng-agent-skills.${agent}.json`;
}

/**
 * What gets copied per agent, relative to the pack root. Sources are an
 * explicit whitelist on purpose: installs must never sweep up whatever
 * happens to sit in a directory (uncommitted files, caches).
 *
 * The skill bodies are CC-BY-4.0 adaptations, so the credit and licence
 * text have to travel with them. The pipeline puts all three inside each
 * bundle's .agents/, so every target that copies .agents carries them
 * automatically. Only claude, which copies the repo's own skills/ tree,
 * names them here.
 */
const NOTICES = ["ATTRIBUTION.md", "NOTICE", "LICENSE", "LICENSE-content"];

const SOURCES: Record<string, { from: string; to: string }[]> = {
  claude: [
    { from: "skills", to: "skills" },
    { from: "commands", to: "commands" },
    { from: "agents", to: "agents" },
    ...NOTICES.map((name) => ({ from: name, to: `skills/${name}` })),
  ],
  copilot: [
    { from: "dist/copilot/.github", to: ".github" },
    { from: "dist/copilot/.agents", to: ".agents" },
  ],
  cursor: [
    { from: "dist/cursor/.cursor", to: ".cursor" },
    { from: "dist/cursor/.agents", to: ".agents" },
  ],
  codex: [
    { from: "dist/codex/AGENTS.md", to: "AGENTS.md" },
    { from: "dist/codex/.agents", to: ".agents" },
    { from: "dist/codex/rseng-check", to: "rseng-check" },
    // The pipeline builds codex hook config into dist/codex/.codex, but this
    // list never copied it, so codex installs silently lost the proactive
    // layer that gemini gets. gemini only works because its source is the
    // whole dist/gemini tree.
    { from: "dist/codex/.codex", to: ".codex" },
  ],
  gemini: [{ from: "dist/gemini", to: "." }],
  // Antigravity has its own built tree, carrying AGENTS.md and no hook
  // config. This pointed at dist/gemini, so antigravity installs shipped
  // no AGENTS.md and pulled in gemini's hooks - which the README promises
  // they do not get.
  antigravity: [{ from: "dist/antigravity", to: "." }],
};

export interface FileCopy {
  from: string;
  to: string;
}

export interface InstallPlan {
  target: AgentTarget;
  copies: FileCopy[];
}

function walkFiles(root: string): string[] {
  const out: string[] = [];
  for (const entry of fs.readdirSync(root, {
    withFileTypes: true,
    recursive: true,
  })) {
    if (entry.isFile()) {
      out.push(path.join(entry.parentPath, entry.name));
    }
  }
  return out;
}

export function sha256(file: string): string {
  return crypto
    .createHash("sha256")
    .update(fs.readFileSync(file))
    .digest("hex");
}

/** Expand the whitelist into concrete file copies for one agent target. */
export function planInstall(
  packRoot: string,
  target: AgentTarget,
): InstallPlan {
  const sources = SOURCES[target.agent];
  if (!sources) {
    throw new Error(`no install sources defined for agent ${target.agent}`);
  }
  const copies: FileCopy[] = [];
  for (const source of sources) {
    const absFrom = path.join(packRoot, source.from);
    if (!fs.existsSync(absFrom)) {
      throw new Error(
        `missing pack content ${source.from} (run the adapter build first)`,
      );
    }
    if (fs.statSync(absFrom).isFile()) {
      copies.push({
        from: absFrom,
        to: path.join(target.installDir, source.to),
      });
      continue;
    }
    for (const file of walkFiles(absFrom)) {
      const rel = path.relative(absFrom, file);
      copies.push({
        from: file,
        to: path.join(target.installDir, source.to, rel),
      });
    }
  }
  return { target, copies };
}

/**
 * Manifest keys are always POSIX-style.
 *
 * path.relative() returns the platform separator, so a manifest written on
 * Windows records "skills\\rseng-testing\\SKILL.md". Read back on macOS or
 * Linux that is one long filename, nothing matches, and update/doctor report
 * every managed file as missing. Normalising on the way in and out keeps a
 * manifest portable across the machines that share a project.
 */
export function toPosixKey(rel: string): string {
  // Split on backslash as well as the platform separator. Depending on
  // path.sep alone made this a no-op on POSIX, so the behaviour was
  // unobservable - and so untestable - anywhere but a Windows runner.
  return rel.split(path.sep).join("/").split("\\").join("/");
}

export function manifestKey(from: string, to: string): string {
  return toPosixKey(path.relative(from, to));
}

export const BACKUP_PREFIX = ".rseng-backup-";

/**
 * Written into a backup that holds the user's own content, so pruning can
 * tell it apart from a routine copy of pack files. Without this, three
 * no-op updates evicted the one backup containing a hand-written AGENTS.md
 * and left three identical copies of our own files in its place.
 */
export const USER_CONTENT_MARKER = ".rseng-your-files";

/** The pack's own version, read from whichever layout the CLI is running in. */
export function packVersion(packRoot: string): string | undefined {
  for (const candidate of [
    path.join(packRoot, "installer", "package.json"),
    path.join(packRoot, "package.json"),
  ]) {
    if (fs.existsSync(candidate)) {
      return JSON.parse(fs.readFileSync(candidate, "utf8")).version;
    }
  }
  return undefined;
}

/**
 * How many backup directories to keep. Each one is a full copy of every
 * managed file, so without a cap they accumulate inside the user's project
 * forever - one per update, unnoticed and ungitignored.
 */
export const BACKUPS_KEPT = 3;

/** Remove all but the newest BACKUPS_KEPT backup directories. */
export function pruneBackups(installDir: string): number {
  let entries: fs.Dirent[];
  try {
    entries = fs.readdirSync(installDir, { withFileTypes: true });
  } catch {
    return 0;
  }
  const backups = entries
    .filter((e) => e.isDirectory() && e.name.startsWith(BACKUP_PREFIX))
    // Never evict a backup holding files we did not put there.
    .filter(
      (e) => !fs.existsSync(path.join(installDir, e.name, USER_CONTENT_MARKER)),
    )
    .map((e) => {
      const abs = path.join(installDir, e.name);
      return { abs, mtime: fs.statSync(abs).mtimeMs };
    })
    .sort((a, b) => b.mtime - a.mtime);
  let removed = 0;
  for (const old of backups.slice(BACKUPS_KEPT)) {
    try {
      fs.rmSync(old.abs, { recursive: true, force: true });
      removed += 1;
    } catch {
      // A backup we cannot remove is not worth failing an update over.
    }
  }
  return removed;
}

/**
 * Destinations holding content this install did not put there: a
 * hand-written AGENTS.md, an existing .gemini/settings.json, or a managed
 * file the user has edited since.
 *
 * Judged on CONTENT, not on whether the manifest lists the path. Checking
 * only for an unknown key protected the first install but not the second:
 * once a file was recorded, re-running install overwrote the user's edits
 * to it silently, while update - which compares hashes - preserved them.
 * Two commands must not differ on whether they destroy your work.
 */
function collisions(plan: InstallPlan): string[] {
  const manifest = readManifest(plan.target.installDir, plan.target.agent);
  const recorded = manifest?.files ?? {};
  const out: string[] = [];
  for (const copy of plan.copies) {
    const rel = manifestKey(plan.target.installDir, copy.to);
    const abs = path.join(plan.target.installDir, rel);
    if (!fs.existsSync(abs)) {
      continue;
    }
    const onDisk = sha256(abs);
    if (recorded[rel] !== undefined && onDisk === recorded[rel]) {
      continue; // ours, untouched
    }
    // Nothing is lost by overwriting a file that already holds exactly the
    // bytes we are about to write. Without this, installing a second agent
    // into a project root the first one shares copied 165 identical files
    // into a backup directory and printed an 8 KB log line.
    if (onDisk === sha256(copy.from)) {
      continue;
    }
    out.push(rel);
  }
  return out.sort();
}

/** Name a few files, then a count - a full list can run to thousands of characters. */
function summarise(paths: string[], shown = 3): string {
  return paths.length <= shown
    ? paths.join(", ")
    : `${paths.slice(0, shown).join(", ")} and ${paths.length - shown} more`;
}

/** Execute a plan and record installed files in a manifest. */
export function executePlan(ctx: CliContext, plan: InstallPlan): void {
  const label = `${plan.target.agent} (${plan.target.scope})`;
  const collided = collisions(plan);
  if (ctx.dryRun) {
    ctx.log(
      `[dry-run] ${label}: would install ${plan.copies.length} files into ${plan.target.installDir}`,
    );
    for (const copy of plan.copies.slice(0, 5)) {
      ctx.log(`[dry-run]   ${path.relative(plan.target.installDir, copy.to)}`);
    }
    if (plan.copies.length > 5) {
      ctx.log(`[dry-run]   ... and ${plan.copies.length - 5} more`);
    }
    if (collided.length > 0) {
      ctx.log(
        `[dry-run] ${label}: would copy ${collided.length} of your own file(s) aside first: ${summarise(collided)}`,
      );
    }
    return;
  }

  // Copy anything of the user's aside before writing over it. Same shape as
  // the update path, so both commands treat the user's own work the same way.
  let backupDir: string | undefined;
  if (collided.length > 0) {
    backupDir = fs.mkdtempSync(
      path.join(plan.target.installDir, BACKUP_PREFIX),
    );
    fs.writeFileSync(
      path.join(backupDir, USER_CONTENT_MARKER),
      "These are your files, saved before the pack overwrote them.\n" +
        "Nothing here was installed by rseng-agent-skills, so it is never\n" +
        "cleaned up automatically. Delete it once you no longer need it.\n",
    );
    for (const rel of collided) {
      const backupPath = path.join(backupDir, rel);
      fs.mkdirSync(path.dirname(backupPath), { recursive: true });
      fs.copyFileSync(path.join(plan.target.installDir, rel), backupPath);
    }
  }

  // Start from what is already recorded and write the manifest whatever
  // happens. Writing it only after the loop meant one EACCES partway
  // through left files updated on disk under their OLD hashes: doctor
  // then called them "user-edited", update preserved them, and re-pinned
  // the stale hashes - a mislabelling no documented command could undo.
  const previous = readManifest(plan.target.installDir, plan.target.agent);
  const manifestFiles: Record<string, string> = { ...(previous?.files ?? {}) };
  const manifestPath = path.join(
    plan.target.installDir,
    manifestName(plan.target.agent),
  );
  // Record the version actually being installed. A literal here meant that
  // from the next release on, doctor compared an old constant against the
  // real pack version and called every fresh install stale.
  const writeManifest = () =>
    fs.writeFileSync(
      manifestPath,
      `${JSON.stringify(
        {
          version: packVersion(ctx.packRoot) ?? "unknown",
          files: manifestFiles,
        },
        null,
        2,
      )}\n`,
    );
  try {
    for (const copy of plan.copies) {
      fs.mkdirSync(path.dirname(copy.to), { recursive: true });
      fs.copyFileSync(copy.from, copy.to);
      manifestFiles[manifestKey(plan.target.installDir, copy.to)] = sha256(
        copy.to,
      );
    }
  } finally {
    writeManifest();
  }
  ctx.log(
    `${label}: installed ${plan.copies.length} files into ${plan.target.installDir}`,
  );
  if (backupDir !== undefined) {
    pruneBackups(plan.target.installDir);
    ctx.log(
      // "kept at" read as though the file had been left alone. install
      // deliberately restores pack content - that is how you get back to a
      // clean copy - so say plainly that it was replaced, and where the
      // previous version is. update is the command that preserves edits.
      `${label}: replaced ${summarise(collided)} - your previous version is in ${path.basename(backupDir)} (use "update" to keep your edits instead)`,
    );
  }
}

/**
 * Resolve a manifest key against the install directory, refusing anything
 * that escapes it.
 *
 * Manifest keys come from a JSON file that lives in the user's project, so
 * they are untrusted input. A key like "../../etc/thing" made update's
 * retired-file cleanup delete outside the install directory entirely. The
 * separator on the prefix matters too: without it, installDir /tmp/x would
 * accept a path under /tmp/xy.
 */
export function resolveInside(
  installDir: string,
  rel: string,
): string | undefined {
  const base = path.resolve(installDir);
  const abs = path.resolve(base, rel);
  const prefix = base.endsWith(path.sep) ? base : base + path.sep;
  return abs.startsWith(prefix) ? abs : undefined;
}

export function readManifest(
  installDir: string,
  agent: string,
): { version: string; files: Record<string, string> } | undefined {
  const manifestPath = path.join(installDir, manifestName(agent));
  if (!fs.existsSync(manifestPath)) {
    return undefined;
  }
  const parsed = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  // Normalise on the way IN as well as out. Manifests written before keys
  // were normalised, or by a Windows build, carry backslash keys; read
  // literally on POSIX every one of them resolves to nothing, doctor calls
  // the whole install missing, and update finds no user-edited files to
  // preserve and overwrites them. Migrating on read costs nothing.
  return {
    ...parsed,
    files: Object.fromEntries(
      Object.entries(parsed.files ?? {})
        .map(([key, hash]) => [key.split("\\").join("/"), hash] as const)
        // Drop anything that would resolve outside the install directory.
        // Filtering here covers every consumer at once - update's deletion
        // path, the collision backup, doctor - instead of trusting each to
        // remember.
        .filter(([key]) => resolveInside(installDir, key) !== undefined),
    ),
  };
}
