import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import type { AgentTarget } from "../src/agents.js";
import type { CliContext } from "../src/context.js";
import { executePlan, manifestName, planInstall } from "../src/install.js";
import { executeUninstall, planUninstall } from "../src/uninstall.js";

let packRoot: string;
let destRoot: string;
let logs: string[];

function write(rel: string, text: string): void {
  const abs = path.join(packRoot, rel);
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, text);
}

function ctx(dryRun = false): CliContext {
  return {
    dryRun,
    packRoot,
    log: (m) => logs.push(m),
    confirm: async () => true,
  };
}

function target(): AgentTarget {
  return {
    agent: "codex",
    scope: "project",
    marker: path.join(destRoot, ".codex"),
    installDir: destRoot,
    detected: true,
  };
}

/** Install first: an uninstall test with nothing installed proves nothing. */
function install(): void {
  executePlan(ctx(), planInstall(packRoot, target()));
}

beforeEach(() => {
  packRoot = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-pack-"));
  destRoot = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-dest-"));
  logs = [];
  write("dist/codex/AGENTS.md", "agents file\n");
  write("dist/codex/.agents/ATTRIBUTION.md", "credit\n");
  write("dist/codex/.agents/NOTICE", "credit\n");
  write("dist/codex/.agents/LICENSE", "mit\n");
  write("dist/codex/.agents/LICENSE-content", "credit\n");
  write("dist/codex/.agents/skills/rseng-testing/SKILL.md", "skill copy\n");
  write("dist/codex/rseng-check/rseng_check.py", "check script\n");
  write("dist/codex/.codex/hooks.json", '{"hooks":{}}\n');
});

afterEach(() => {
  fs.rmSync(packRoot, { recursive: true, force: true });
  fs.rmSync(destRoot, { recursive: true, force: true });
});

describe("planUninstall", () => {
  it("classifies recorded files by whether they are still ours", () => {
    install();
    const skill = path.join(
      destRoot,
      ".agents",
      "skills",
      "rseng-testing",
      "SKILL.md",
    );
    fs.appendFileSync(skill, "my own notes\n");
    fs.rmSync(path.join(destRoot, "AGENTS.md"));

    const plan = planUninstall(target());
    expect(plan.edited).toEqual([
      path.join(".agents", "skills", "rseng-testing", "SKILL.md"),
    ]);
    expect(plan.absent).toEqual(["AGENTS.md"]);
    expect(plan.managed.length).toBeGreaterThan(0);
    expect(plan.managed).not.toContain("AGENTS.md");
  });

  it("considers nothing when there is no manifest", () => {
    const plan = planUninstall(target());
    expect(plan.managed).toEqual([]);
    expect(plan.edited).toEqual([]);
  });

  it("never looks beyond the manifest", () => {
    // An uninstall that walked the install directory would take a file
    // the user happened to put under a name the pack also uses.
    install();
    const mine = path.join(destRoot, ".agents", "skills", "my-notes.md");
    fs.writeFileSync(mine, "not the pack's\n");

    executeUninstall(ctx(), planUninstall(target()));
    expect(fs.existsSync(mine)).toBe(true);
  });
});

describe("executeUninstall", () => {
  it("removes what it installed and leaves the tree clean", () => {
    install();
    const result = executeUninstall(ctx(), planUninstall(target()));
    expect(result.kept).toEqual([]);
    expect(fs.readdirSync(destRoot)).toEqual([]);
  });

  it("keeps user-edited files, and the manifest that explains them", () => {
    install();
    const skill = path.join(
      destRoot,
      ".agents",
      "skills",
      "rseng-testing",
      "SKILL.md",
    );
    fs.appendFileSync(skill, "my own notes\n");

    const result = executeUninstall(ctx(), planUninstall(target()));
    expect(result.kept).toHaveLength(1);
    expect(fs.readFileSync(skill, "utf8")).toContain("my own notes");
    // Removing the manifest here would strand the file with no record of
    // where it came from, and make `doctor` blind to it.
    expect(fs.existsSync(path.join(destRoot, manifestName("codex")))).toBe(
      true,
    );
  });

  it("removes edited files only when forced", () => {
    install();
    const skill = path.join(
      destRoot,
      ".agents",
      "skills",
      "rseng-testing",
      "SKILL.md",
    );
    fs.appendFileSync(skill, "my own notes\n");

    executeUninstall(ctx(), planUninstall(target()), { force: true });
    expect(fs.existsSync(skill)).toBe(false);
    expect(fs.readdirSync(destRoot)).toEqual([]);
  });

  it("writes nothing on a dry run", () => {
    install();
    const before = fs.readdirSync(destRoot).sort();
    const result = executeUninstall(ctx(true), planUninstall(target()));
    expect(result.removed).toBeGreaterThan(0);
    expect(fs.readdirSync(destRoot).sort()).toEqual(before);
    expect(logs.join("\n")).toContain("would remove");
  });

  it("names the files it keeps rather than dropping them silently", () => {
    install();
    fs.appendFileSync(
      path.join(destRoot, ".agents", "skills", "rseng-testing", "SKILL.md"),
      "my own notes\n",
    );
    executeUninstall(ctx(), planUninstall(target()));
    expect(logs.join("\n")).toContain("rseng-testing");
  });
});
