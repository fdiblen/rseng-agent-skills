import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import type { AgentTarget } from "../src/agents.js";
import type { CliContext } from "../src/context.js";
import {
  MANIFEST_NAME,
  executePlan,
  planInstall,
  readManifest,
} from "../src/install.js";

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

function cursorTarget(): AgentTarget {
  return {
    agent: "cursor",
    scope: "project",
    marker: path.join(destRoot, ".cursor"),
    installDir: path.join(destRoot, ".cursor", "rules"),
    detected: true,
  };
}

beforeEach(() => {
  packRoot = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-pack-"));
  destRoot = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-dest-"));
  logs = [];
  write("skills/taxonomy.yml", "skills: {}\n");
  write("skills/rseng-testing/SKILL.md", "---\nname: rseng-testing\n---\n");
  write("dist/cursor/.cursor/rules/rseng-overview.mdc", "rule one\n");
  write("dist/cursor/.cursor/rules/rseng-testing.mdc", "rule two\n");
  write("dist/codex/AGENTS.md", "agents file\n");
  write("dist/codex/skills/rseng-testing/SKILL.md", "skill copy\n");
});

afterEach(() => {
  fs.rmSync(packRoot, { recursive: true, force: true });
  fs.rmSync(destRoot, { recursive: true, force: true });
});

describe("planInstall", () => {
  it("expands the cursor whitelist into file copies", () => {
    const plan = planInstall(packRoot, cursorTarget());
    const dests = plan.copies.map((c) =>
      path.relative(cursorTarget().installDir, c.to),
    );
    expect(dests.sort()).toEqual([
      "rseng-overview.mdc",
      "rseng-testing.mdc",
    ]);
  });

  it("handles single-file sources (codex AGENTS.md)", () => {
    const target: AgentTarget = {
      agent: "codex",
      scope: "user",
      marker: destRoot,
      installDir: destRoot,
      detected: true,
    };
    const plan = planInstall(packRoot, target);
    const dests = plan.copies.map((c) => path.relative(destRoot, c.to)).sort();
    expect(dests).toEqual([
      "AGENTS.md",
      path.join("skills", "rseng-testing", "SKILL.md"),
    ]);
  });

  it("fails clearly when adapter output is missing", () => {
    fs.rmSync(path.join(packRoot, "dist"), { recursive: true });
    expect(() => planInstall(packRoot, cursorTarget())).toThrow(
      /run the adapter build first/,
    );
  });
});

describe("executePlan", () => {
  it("copies files and writes a manifest with hashes", () => {
    const target = cursorTarget();
    executePlan(ctx(), planInstall(packRoot, target));
    expect(
      fs.existsSync(path.join(target.installDir, "rseng-overview.mdc")),
    ).toBe(true);
    const manifest = readManifest(target.installDir);
    expect(Object.keys(manifest?.files ?? {}).sort()).toEqual([
      "rseng-overview.mdc",
      "rseng-testing.mdc",
    ]);
    for (const hash of Object.values(manifest?.files ?? {})) {
      expect(hash).toMatch(/^[0-9a-f]{64}$/);
    }
  });

  it("writes nothing in dry-run mode", () => {
    const target = cursorTarget();
    executePlan(ctx(true), planInstall(packRoot, target));
    expect(fs.existsSync(target.installDir)).toBe(false);
    expect(logs.some((l) => l.includes("[dry-run]"))).toBe(true);
  });

  it("readManifest returns undefined before any install", () => {
    expect(readManifest(destRoot)).toBeUndefined();
    expect(fs.existsSync(path.join(destRoot, MANIFEST_NAME))).toBe(false);
  });
});
