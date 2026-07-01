import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import type { AgentTarget } from "../src/agents.js";
import type { CliContext } from "../src/context.js";
import { executePlan, planInstall, readManifest } from "../src/install.js";
import { executeUpdate } from "../src/update.js";

let packRoot: string;
let destRoot: string;
let logs: string[];

function write(rel: string, text: string): void {
  const abs = path.join(packRoot, rel);
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, text);
}

function ctx(dryRun = false): CliContext {
  return { dryRun, packRoot, log: (m) => logs.push(m) };
}

function target(): AgentTarget {
  return {
    agent: "cursor",
    scope: "project",
    marker: path.join(destRoot, ".cursor"),
    installDir: path.join(destRoot, ".cursor"),
    detected: true,
  };
}

beforeEach(() => {
  packRoot = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-pack-"));
  destRoot = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-dest-"));
  logs = [];
  write("AGENTS.md", "pack umbrella\n");
  write("skills/.keep", "");
  write("dist/cursor/.cursor/rules/one.mdc", "rule one v1\n");
  write("dist/cursor/.cursor/rules/two.mdc", "rule two v1\n");
  executePlan(ctx(), planInstall(packRoot, target()));
});

afterEach(() => {
  fs.rmSync(packRoot, { recursive: true, force: true });
  fs.rmSync(destRoot, { recursive: true, force: true });
});

describe("executeUpdate", () => {
  it("replaces managed files with new content", () => {
    write("dist/cursor/.cursor/rules/one.mdc", "rule one v2\n");
    const result = executeUpdate(ctx(), planInstall(packRoot, target()));
    expect(result.updated).toBe(2);
    expect(result.preserved).toEqual([]);
    const updated = fs.readFileSync(
      path.join(target().installDir, "rules", "one.mdc"),
      "utf8",
    );
    expect(updated).toBe("rule one v2\n");
  });

  it("preserves user-edited files and reports them", () => {
    const edited = path.join(target().installDir, "rules", "two.mdc");
    fs.writeFileSync(edited, "my local customization\n");
    write("dist/cursor/.cursor/rules/two.mdc", "rule two v2\n");

    const result = executeUpdate(ctx(), planInstall(packRoot, target()));
    expect(result.preserved).toEqual([path.join("rules", "two.mdc")]);
    expect(fs.readFileSync(edited, "utf8")).toBe("my local customization\n");
    // The preserved file's manifest hash now matches its edited content,
    // so a second update still leaves it alone.
    const again = executeUpdate(ctx(), planInstall(packRoot, target()));
    expect(again.preserved).toEqual([path.join("rules", "two.mdc")]);
  });

  it("backs up managed files before replacing", () => {
    write("dist/cursor/.cursor/rules/one.mdc", "rule one v2\n");
    const result = executeUpdate(ctx(), planInstall(packRoot, target()));
    expect(result.backupDir).toBeDefined();
    const backup = fs.readFileSync(
      path.join(result.backupDir as string, "rules", "one.mdc"),
      "utf8",
    );
    expect(backup).toBe("rule one v1\n");
  });

  it("dry-run reports without touching anything", () => {
    write("dist/cursor/.cursor/rules/one.mdc", "rule one v2\n");
    executeUpdate(ctx(true), planInstall(packRoot, target()));
    const current = fs.readFileSync(
      path.join(target().installDir, "rules", "one.mdc"),
      "utf8",
    );
    expect(current).toBe("rule one v1\n");
    expect(logs.some((l) => l.includes("[dry-run]"))).toBe(true);
  });

  it("refuses to update without a manifest", () => {
    fs.rmSync(path.join(target().installDir, ".rseng-agent-skills.json"));
    expect(() => executeUpdate(ctx(), planInstall(packRoot, target()))).toThrow(
      /run install first/,
    );
    expect(readManifest(target().installDir)).toBeUndefined();
  });
});
