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
  backupDir?: string;
  prunedBackups?: number;
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

  if (ctx.dryRun) {
    ctx.log(
      `[dry-run] ${plan.target.agent}: would update ${managed.length} managed files` +
        (preserved.length > 0
          ? `, preserving ${preserved.length} user-edited: ${preserved.join(", ")}`
          : ""),
    );
    return { updated: managed.length, preserved };
  }

  const backupDir = fs.mkdtempSync(path.join(installDir, BACKUP_PREFIX));
  for (const rel of managed) {
    const abs = path.join(installDir, rel);
    if (fs.existsSync(abs)) {
      const backupPath = path.join(backupDir, rel);
      fs.mkdirSync(path.dirname(backupPath), { recursive: true });
      fs.copyFileSync(abs, backupPath);
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
  const prunedBackups = pruneBackups(installDir);
  ctx.log(`${plan.target.agent}: backup at ${backupDir}`);
  if (prunedBackups > 0) {
    ctx.log(
      `${plan.target.agent}: removed ${prunedBackups} older backup(s), keeping ${BACKUPS_KEPT}`,
    );
  }
  return {
    updated: filteredPlan.copies.length,
    preserved,
    backupDir,
    prunedBackups,
  };
}
