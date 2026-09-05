import fs from "node:fs";
import path from "node:path";
import type { AgentTarget } from "./agents.js";
import type { CliContext } from "./context.js";
import { manifestName, readManifest, sha256, summarise } from "./install.js";

export interface UninstallPlan {
  target: AgentTarget;
  /** Recorded files still byte-identical to what we wrote. */
  managed: string[];
  /** Recorded files the user has since changed. */
  edited: string[];
  /** Recorded files already gone from disk. */
  absent: string[];
}

export interface UninstallResult {
  removed: number;
  kept: string[];
}

/**
 * What an uninstall would touch, from the manifest alone.
 *
 * The manifest records a hash per file, so a file that still matches is
 * demonstrably ours and safe to delete, while one that does not is the
 * user's work under a name we happen to have written. Nothing outside
 * the manifest is ever considered - an uninstall that walked the install
 * directory would take a neighbouring file with a familiar name.
 */
export function planUninstall(target: AgentTarget): UninstallPlan {
  const manifest = readManifest(target.installDir, target.agent);
  const plan: UninstallPlan = {
    target,
    managed: [],
    edited: [],
    absent: [],
  };
  if (!manifest) {
    return plan;
  }
  for (const [rel, recorded] of Object.entries(manifest.files)) {
    const abs = path.join(target.installDir, rel);
    if (!fs.existsSync(abs)) {
      plan.absent.push(rel);
    } else if (sha256(abs) === recorded) {
      plan.managed.push(rel);
    } else {
      plan.edited.push(rel);
    }
  }
  return plan;
}

/** Drop directories the removal left empty, never climbing past installDir. */
function pruneEmptyDirs(installDir: string, rel: string): void {
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
 * Remove one agent's install. Files the user has edited are left alone
 * unless `force` is set, and are named either way so nothing disappears
 * without being mentioned.
 */
export function executeUninstall(
  ctx: CliContext,
  plan: UninstallPlan,
  options: { force?: boolean } = {},
): UninstallResult {
  const { target } = plan;
  const label = `${target.agent} (${target.scope})`;
  const doomed = options.force
    ? [...plan.managed, ...plan.edited]
    : plan.managed;
  const kept = options.force ? [] : plan.edited;

  if (ctx.dryRun) {
    ctx.log(
      `${label}: would remove ${doomed.length} file(s) from ${target.installDir}`,
    );
    if (kept.length > 0) {
      ctx.log(`${label}: would keep ${summarise(kept)} (edited since install)`);
    }
    return { removed: doomed.length, kept };
  }

  for (const rel of doomed) {
    const abs = path.join(target.installDir, rel);
    try {
      fs.rmSync(abs, { force: true });
    } catch {
      // A file we cannot delete is not worth aborting the rest for.
      continue;
    }
    pruneEmptyDirs(target.installDir, rel);
  }

  // The manifest goes last, and only once nothing it records is left to
  // remove: deleting it first would strand every remaining file with no
  // record of where it came from.
  if (kept.length === 0) {
    fs.rmSync(path.join(target.installDir, manifestName(target.agent)), {
      force: true,
    });
  }

  ctx.log(
    `${label}: removed ${doomed.length} file(s) from ${target.installDir}`,
  );
  if (kept.length > 0) {
    ctx.log(
      `${label}: kept ${summarise(kept)} - edited since install, and the ` +
        `manifest with them. Pass --force to remove these too.`,
    );
  }
  return { removed: doomed.length, kept };
}
