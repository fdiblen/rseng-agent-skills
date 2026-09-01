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
 */
/**
 * The skill bodies are CC-BY-4.0 adaptations, so the credit and licence
 * text have to travel with them. gemini and antigravity copy a whole
 * dist/ tree and pick these up from its root; the targets below copy
 * selected subtrees, so they name the notices explicitly and land them
 * beside the skills rather than in the user's project root.
 */
const NOTICES = ["ATTRIBUTION.md", "NOTICE", "LICENSE-content"];

const notices = (from: string, to: string) =>
  NOTICES.map((name) => ({ from: `${from}/${name}`, to: `${to}/${name}` }));

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
    ...notices("dist/copilot", ".agents"),
  ],
  cursor: [
    { from: "dist/cursor/.cursor", to: ".cursor" },
    { from: "dist/cursor/.agents", to: ".agents" },
    ...notices("dist/cursor", ".agents"),
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
    ...notices("dist/codex", ".agents"),
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

/** Execute a plan and record installed files in a manifest. */
/**
 * Manifest keys are always POSIX-style.
 *
 * path.relative() returns the platform separator, so a manifest written on
 * Windows records "skills\\rseng-testing\\SKILL.md". Read back on macOS or
 * Linux that is one long filename, nothing matches, and update/doctor report
 * every managed file as missing. Normalising on the way in and out keeps a
 * manifest portable across the machines that share a project.
 */
export function manifestKey(from: string, to: string): string {
  return path.relative(from, to).split(path.sep).join("/");
}

export const BACKUP_PREFIX = ".rseng-backup-";

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
 * Destinations that already exist but this agent's manifest does not claim -
 * a hand-written AGENTS.md, an existing .gemini/settings.json. update()
 * protects files it installed; nothing protected files it never installed,
 * so a first install overwrote them with no backup and no mention.
 */
function unmanagedCollisions(plan: InstallPlan): string[] {
  const manifest = readManifest(plan.target.installDir, plan.target.agent);
  const managed = new Set(Object.keys(manifest?.files ?? {}));
  return plan.copies
    .map((copy) => manifestKey(plan.target.installDir, copy.to))
    .filter(
      (rel) =>
        !managed.has(rel) &&
        fs.existsSync(path.join(plan.target.installDir, rel)),
    )
    .sort();
}

export function executePlan(ctx: CliContext, plan: InstallPlan): void {
  const label = `${plan.target.agent} (${plan.target.scope})`;
  const collisions = unmanagedCollisions(plan);
  if (ctx.dryRun) {
    ctx.log(`[dry-run] ${label}: would install ${plan.copies.length} files`);
    for (const copy of plan.copies.slice(0, 5)) {
      ctx.log(`[dry-run]   ${path.relative(plan.target.installDir, copy.to)}`);
    }
    if (plan.copies.length > 5) {
      ctx.log(`[dry-run]   ... and ${plan.copies.length - 5} more`);
    }
    if (collisions.length > 0) {
      ctx.log(
        `[dry-run] ${label}: would copy ${collisions.length} of your own file(s) aside first: ${collisions.join(", ")}`,
      );
    }
    return;
  }

  // Copy anything of the user's aside before writing over it. Same shape as
  // the update path, so both commands treat the user's own work the same way.
  let backupDir: string | undefined;
  if (collisions.length > 0) {
    backupDir = fs.mkdtempSync(
      path.join(plan.target.installDir, BACKUP_PREFIX),
    );
    for (const rel of collisions) {
      const backupPath = path.join(backupDir, rel);
      fs.mkdirSync(path.dirname(backupPath), { recursive: true });
      fs.copyFileSync(path.join(plan.target.installDir, rel), backupPath);
    }
  }

  const manifestFiles: Record<string, string> = {};
  for (const copy of plan.copies) {
    fs.mkdirSync(path.dirname(copy.to), { recursive: true });
    fs.copyFileSync(copy.from, copy.to);
    manifestFiles[manifestKey(plan.target.installDir, copy.to)] = sha256(
      copy.to,
    );
  }
  const manifestPath = path.join(
    plan.target.installDir,
    manifestName(plan.target.agent),
  );
  // Record the version actually being installed. A literal here meant that
  // from the next release on, doctor compared an old constant against the
  // real pack version and called every fresh install stale.
  fs.writeFileSync(
    manifestPath,
    `${JSON.stringify(
      { version: packVersion(ctx.packRoot) ?? "unknown", files: manifestFiles },
      null,
      2,
    )}\n`,
  );
  ctx.log(`${label}: installed ${plan.copies.length} files`);
  if (backupDir !== undefined) {
    ctx.log(
      `${label}: your existing ${collisions.join(", ")} kept at ${path.basename(backupDir)}`,
    );
  }
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
      Object.entries(parsed.files ?? {}).map(([key, hash]) => [
        key.split("\\").join("/"),
        hash,
      ]),
    ),
  };
}
