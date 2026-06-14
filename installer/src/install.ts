import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import type { AgentTarget } from "./agents.js";
import type { CliContext } from "./context.js";

export const MANIFEST_NAME = ".rseng-agent-skills.json";

/**
 * What gets copied per agent, relative to the pack root. Sources are an
 * explicit whitelist on purpose: installs must never sweep up whatever
 * happens to sit in a directory (uncommitted files, caches).
 */
const SOURCES: Record<string, { from: string; to: string }[]> = {
  claude: [
    { from: "skills", to: "skills" },
    { from: "commands", to: "commands" },
    { from: "agents", to: "agents" },
  ],
  copilot: [{ from: "dist/copilot/.github", to: "." }],
  cursor: [{ from: "dist/cursor/.cursor/rules", to: "." }],
  codex: [
    { from: "dist/codex/AGENTS.md", to: "AGENTS.md" },
    { from: "dist/codex/skills", to: "skills" },
  ],
  gemini: [{ from: "dist/gemini", to: "." }],
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
export function executePlan(ctx: CliContext, plan: InstallPlan): void {
  const label = `${plan.target.agent} (${plan.target.scope})`;
  if (ctx.dryRun) {
    ctx.log(`[dry-run] ${label}: would install ${plan.copies.length} files`);
    for (const copy of plan.copies.slice(0, 5)) {
      ctx.log(`[dry-run]   ${path.relative(plan.target.installDir, copy.to)}`);
    }
    if (plan.copies.length > 5) {
      ctx.log(`[dry-run]   ... and ${plan.copies.length - 5} more`);
    }
    return;
  }
  const manifestFiles: Record<string, string> = {};
  for (const copy of plan.copies) {
    fs.mkdirSync(path.dirname(copy.to), { recursive: true });
    fs.copyFileSync(copy.from, copy.to);
    manifestFiles[path.relative(plan.target.installDir, copy.to)] = sha256(
      copy.to,
    );
  }
  const manifestPath = path.join(plan.target.installDir, MANIFEST_NAME);
  fs.writeFileSync(
    manifestPath,
    `${JSON.stringify({ version: "0.1.0", files: manifestFiles }, null, 2)}\n`,
  );
  ctx.log(`${label}: installed ${plan.copies.length} files`);
}

export function readManifest(
  installDir: string,
): { version: string; files: Record<string, string> } | undefined {
  const manifestPath = path.join(installDir, MANIFEST_NAME);
  if (!fs.existsSync(manifestPath)) {
    return undefined;
  }
  return JSON.parse(fs.readFileSync(manifestPath, "utf8"));
}
