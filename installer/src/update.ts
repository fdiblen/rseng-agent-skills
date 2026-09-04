import fs from "node:fs";
import path from "node:path";
import type { CliContext } from "./context.js";
import {
  BACKUP_PREFIX,
  BACKUPS_KEPT,
  executePlan,
  type InstallPlan,
  manifestKey,
  manifestName,
  pruneBackups,
  readManifest,
  sha256,
} from "./install.js";

export interface UpdateResult {
  updated: number;
  preserved: string[];
  removed: string[];
  backupDir?: string;
  prunedBackups?: number;
}

/** Drop directories left empty after a retired file was removed. */
function pruneEmptyDirs(installDir: string, rel: string): void {
  // Compare with the separator appended: a bare prefix test would treat
  // /tmp/xy as living inside /tmp/x. readManifest already refuses keys that
  // escape, so this is the second lock on the same door.
  const base = path.resolve(installDir);
  const prefix = base.endsWith(path.sep) ? base : base + path.sep;
  let dir = path.dirname(path.resolve(base, rel));
  while (dir.startsWith(prefix) && dir !== base) {
    try {
      if (fs.readdirSync(dir).length > 0) {
        return;
      }
      fs.rmdirSync(dir);
    } catch {
      return;
    }
    dir = path.dirname(dir);
  }
}

/**
 * Update an existing install. Only files the manifest still owns (their
 * on-disk hash matches the recorded one) are replaced; files a user has
 * edited are preserved and reported. The previous state of every managed
 * file is backed up before anything changes.
 */
export function executeUpdate(
  ctx: CliContext,
  plan: InstallPlan,
): UpdateResult {
  const installDir = plan.target.installDir;
  const manifest = readManifest(installDir, plan.target.agent);
  if (!manifest) {
    throw new Error(
      `${installDir} has no ${manifestName(plan.target.agent)}; run install first`,
    );
  }

  const preserved: string[] = [];
  const managed: string[] = [];
  for (const [rel, recordedHash] of Object.entries(manifest.files)) {
    const abs = path.join(installDir, rel);
    if (fs.existsSync(abs) && sha256(abs) !== recordedHash) {
      preserved.push(rel);
    } else {
      managed.push(rel);
    }
  }

  // Files this release no longer ships. The manifest is rebuilt from the new
  // plan, so without this they drop out of the record while staying on disk:
  // untracked forever, and invisible to doctor, which only walks manifest
  // keys. Rename a skill file upstream and every existing install keeps the
  // stale copy. Remove only what is still byte-identical to what we put
  // there - anything edited since is the user's and stays.
  const planned = new Set(
    plan.copies.map((copy) => manifestKey(installDir, copy.to)),
  );
  // Another agent installed into the same directory may still own the
  // file. codex, cursor, copilot, gemini and antigravity all install into
  // the project root and all write .agents/**, each under its own
  // manifest, so updating one used to delete files the others still list
  // and leave them reporting MISSING with no remedy.
  const claimedElsewhere = new Set<string>();
  for (const entry of fs.readdirSync(installDir)) {
    const other = /^\.rseng-agent-skills\.(.+)\.json$/.exec(entry)?.[1];
    if (other === undefined || other === plan.target.agent) {
      continue;
    }
    for (const rel of Object.keys(
      readManifest(installDir, other)?.files ?? {},
    )) {
      claimedElsewhere.add(rel);
    }
  }

  const retired = Object.keys(manifest.files)
    .filter((rel) => !planned.has(rel) && !claimedElsewhere.has(rel))
    .filter((rel) => {
      const abs = path.join(installDir, rel);
      return fs.existsSync(abs) && sha256(abs) === manifest.files[rel];
    })
    .sort();

  if (ctx.dryRun) {
    ctx.log(
      `[dry-run] ${plan.target.agent}: would update ${managed.length} managed files` +
        (preserved.length > 0
          ? `, preserving ${preserved.length} user-edited: ${preserved.join(", ")}`
          : "") +
        (retired.length > 0
          ? `, removing ${retired.length} no longer shipped: ${retired.join(", ")}`
          : ""),
    );
    return { updated: managed.length, preserved, removed: retired };
  }

  // Only back up what is actually about to change. Backing up all 181
  // managed files on every run - including a complete no-op - meant three
  // routine updates aged out the backup that held the user's own files.
  const incoming = new Map(
    plan.copies.map((c) => [manifestKey(installDir, c.to), c.from]),
  );
  const changing = managed.filter((rel) => {
    const abs = path.join(installDir, rel);
    if (!fs.existsSync(abs)) {
      return true; // missing: update restores it
    }
    const from = incoming.get(rel);
    return from === undefined || sha256(abs) !== sha256(from);
  });

  let backupDir: string | undefined;
  if (changing.length > 0) {
    backupDir = fs.mkdtempSync(path.join(installDir, BACKUP_PREFIX));
    for (const rel of changing) {
      const abs = path.join(installDir, rel);
      if (fs.existsSync(abs)) {
        const backupPath = path.join(backupDir, rel);
        fs.mkdirSync(path.dirname(backupPath), { recursive: true });
        fs.copyFileSync(abs, backupPath);
      }
    }
  }

  // Install the new content, skipping preserved files so user edits win.
  const filteredPlan: InstallPlan = {
    target: plan.target,
    copies: plan.copies.filter(
      // preserved holds manifest keys, which are POSIX-style; comparing a
      // platform-separator path here would never match on Windows and the
      // user's edited files would be overwritten.
      (copy) => !preserved.includes(manifestKey(installDir, copy.to)),
    ),
  };
  executePlan(ctx, filteredPlan);

  for (const rel of retired) {
    try {
      fs.rmSync(path.join(installDir, rel), { force: true });
      pruneEmptyDirs(installDir, rel);
    } catch {
      // A file we cannot remove is not worth failing the update over; it
      // stays on disk exactly as it did before.
    }
  }

  // Preserved files keep their ORIGINAL recorded hash: the manifest must
  // keep remembering what the pack installed, so the file still counts as
  // user-edited (and stays protected) on every future update.
  const written = readManifest(installDir, plan.target.agent);
  if (written) {
    for (const rel of preserved) {
      const original = manifest.files[rel];
      if (original !== undefined) {
        written.files[rel] = original;
      }
    }
    fs.writeFileSync(
      path.join(installDir, manifestName(plan.target.agent)),
      `${JSON.stringify(written, null, 2)}\n`,
    );
  }

  if (preserved.length > 0) {
    ctx.log(
      `${plan.target.agent}: preserved user-edited files: ${preserved.join(", ")}`,
    );
  }
  if (retired.length > 0) {
    ctx.log(
      `${plan.target.agent}: removed ${retired.length} file(s) this release no longer ships: ${retired.join(", ")}`,
    );
  }
  const prunedBackups = pruneBackups(installDir);
  if (backupDir !== undefined) {
    ctx.log(`${plan.target.agent}: backup at ${backupDir}`);
  }
  if (prunedBackups > 0) {
    ctx.log(
      `${plan.target.agent}: removed ${prunedBackups} older backup(s), keeping ${BACKUPS_KEPT}`,
    );
  }
  return {
    updated: filteredPlan.copies.length,
    preserved,
    removed: retired,
    backupDir,
    prunedBackups,
  };
}
