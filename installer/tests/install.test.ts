import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import type { AgentTarget } from "../src/agents.js";
import type { CliContext } from "../src/context.js";
import {
  executePlan,
  manifestName,
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
    installDir: destRoot,
    detected: true,
  };
}

beforeEach(() => {
  packRoot = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-pack-"));
  destRoot = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-dest-"));
  logs = [];
  write("AGENTS.md", "pack umbrella\n");
  write("skills/.keep", "");
  write("skills/rseng-testing/SKILL.md", "---\nname: rseng-testing\n---\n");
  write("commands/rseng-check.md", "check command\n");
  write("agents/rseng-reviewer.md", "reviewer agent\n");
  write("notes/some-page.md", "not part of any install\n");
  // The notices travel with CC-BY content, so planInstall requires them.
  write("ATTRIBUTION.md", "credit\n");
  write("NOTICE", "credit\n");
  write("LICENSE-content", "credit\n");
  write("dist/cursor/ATTRIBUTION.md", "credit\n");
  write("dist/cursor/NOTICE", "credit\n");
  write("dist/cursor/LICENSE-content", "credit\n");
  write("dist/codex/ATTRIBUTION.md", "credit\n");
  write("dist/codex/NOTICE", "credit\n");
  write("dist/codex/LICENSE-content", "credit\n");
  write("dist/cursor/.cursor/rules/rseng-overview.mdc", "rule one\n");
  write("dist/cursor/.cursor/rules/rseng-testing.mdc", "rule two\n");
  write("dist/cursor/.agents/skills/rseng-testing/SKILL.md", "native skill\n");
  write("dist/cursor/stray-notes.md", "not whitelisted\n");
  write("dist/codex/AGENTS.md", "agents file\n");
  write("dist/codex/.agents/skills/rseng-testing/SKILL.md", "skill copy\n");
  write("dist/codex/rseng-check/rseng_check.py", "check script\n");
  write("dist/codex/.codex/hooks.json", '{"hooks":{}}\n');
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
      path.join(".agents", "ATTRIBUTION.md"),
      path.join(".agents", "LICENSE-content"),
      path.join(".agents", "NOTICE"),
      path.join(".agents", "skills", "rseng-testing", "SKILL.md"),
      path.join(".cursor", "rules", "rseng-overview.mdc"),
      path.join(".cursor", "rules", "rseng-testing.mdc"),
    ]);
    // Whitelist only: files sitting next to whitelisted dirs are not swept.
    expect(dests.some((d) => d.includes("stray-notes"))).toBe(false);
  });

  it("handles single-file sources (codex AGENTS.md)", () => {
    const target: AgentTarget = {
      agent: "codex",
      scope: "project",
      marker: path.join(destRoot, ".codex"),
      installDir: destRoot,
      detected: true,
    };
    const plan = planInstall(packRoot, target);
    const dests = plan.copies.map((c) => path.relative(destRoot, c.to)).sort();
    expect(dests).toEqual([
      path.join(".agents", "ATTRIBUTION.md"),
      path.join(".agents", "LICENSE-content"),
      path.join(".agents", "NOTICE"),
      path.join(".agents", "skills", "rseng-testing", "SKILL.md"),
      path.join(".codex", "hooks.json"),
      "AGENTS.md",
      path.join("rseng-check", "rseng_check.py"),
    ]);
  });

  it("installs skills, commands and agents for claude", () => {
    const target: AgentTarget = {
      agent: "claude",
      scope: "project",
      marker: path.join(destRoot, ".claude"),
      installDir: path.join(destRoot, ".claude"),
      detected: true,
    };
    const plan = planInstall(packRoot, target);
    const dests = plan.copies
      .map((c) => path.relative(target.installDir, c.to))
      .sort();
    expect(dests).toEqual([
      path.join("agents", "rseng-reviewer.md"),
      path.join("commands", "rseng-check.md"),
      path.join("skills", ".keep"),
      path.join("skills", "ATTRIBUTION.md"),
      path.join("skills", "LICENSE-content"),
      path.join("skills", "NOTICE"),
      path.join("skills", "rseng-testing", "SKILL.md"),
    ]);
    // Whitelist only: nothing outside skills/commands/agents is swept up.
    expect(dests.some((d) => d.includes("notes"))).toBe(false);
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
      fs.existsSync(
        path.join(target.installDir, ".cursor", "rules", "rseng-overview.mdc"),
      ),
    ).toBe(true);
    const manifest = readManifest(target.installDir, "cursor");
    expect(Object.keys(manifest?.files ?? {}).sort()).toEqual([
      path.join(".agents", "ATTRIBUTION.md"),
      path.join(".agents", "LICENSE-content"),
      path.join(".agents", "NOTICE"),
      path.join(".agents", "skills", "rseng-testing", "SKILL.md"),
      path.join(".cursor", "rules", "rseng-overview.mdc"),
      path.join(".cursor", "rules", "rseng-testing.mdc"),
    ]);
    for (const hash of Object.values(manifest?.files ?? {})) {
      expect(hash).toMatch(/^[0-9a-f]{64}$/);
    }
  });

  it("names the manifest after the agent so unified targets coexist", () => {
    const target = cursorTarget();
    executePlan(ctx(), planInstall(packRoot, target));
    expect(
      fs.existsSync(
        path.join(target.installDir, ".rseng-agent-skills.cursor.json"),
      ),
    ).toBe(true);
    expect(readManifest(target.installDir, "codex")).toBeUndefined();
  });

  it("writes nothing in dry-run mode", () => {
    const target = cursorTarget();
    executePlan(ctx(true), planInstall(packRoot, target));
    expect(fs.existsSync(path.join(target.installDir, ".cursor"))).toBe(false);
    expect(fs.existsSync(path.join(target.installDir, ".agents"))).toBe(false);
    expect(readManifest(target.installDir, "cursor")).toBeUndefined();
    expect(logs.some((l) => l.includes("[dry-run]"))).toBe(true);
  });

  it("readManifest returns undefined before any install", () => {
    expect(readManifest(destRoot, "cursor")).toBeUndefined();
    expect(fs.existsSync(path.join(destRoot, manifestName("cursor")))).toBe(
      false,
    );
  });
});

describe("manifest portability", () => {
  it("records POSIX-style keys whatever the platform separator is", () => {
    const target: AgentTarget = {
      agent: "claude",
      scope: "project",
      marker: path.join(destRoot, ".claude"),
      installDir: destRoot,
      detected: true,
    };
    executePlan(ctx(), planInstall(packRoot, target));
    const keys = Object.keys(readManifest(destRoot, "claude")?.files ?? {});
    expect(keys.length).toBeGreaterThan(0);
    expect(keys.some((k) => k.includes("\\"))).toBe(false);
    expect(keys.some((k) => k.includes("/"))).toBe(true);
  });

  it("migrates a manifest written with backslash keys", () => {
    // The real regression: on POSIX path.relative already returns "/", so
    // asserting "no backslashes" passes with or without the normalisation.
    // Only a manifest that ALREADY holds backslash keys - one written by an
    // older build, or on Windows - exercises the read path. Without it,
    // every file reads as missing and update overwrites user edits.
    const target: AgentTarget = {
      agent: "claude",
      scope: "project",
      marker: path.join(destRoot, ".claude"),
      installDir: destRoot,
      detected: true,
    };
    executePlan(ctx(), planInstall(packRoot, target));
    const manifestPath = path.join(destRoot, manifestName("claude"));
    const original = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
    const windowsStyle = {
      ...original,
      files: Object.fromEntries(
        Object.entries(original.files).map(([k, v]) => [
          k.split("/").join("\\"),
          v,
        ]),
      ),
    };
    fs.writeFileSync(manifestPath, JSON.stringify(windowsStyle, null, 2));

    const migrated = readManifest(destRoot, "claude");
    expect(Object.keys(migrated?.files ?? {})).toEqual(
      Object.keys(original.files),
    );
    for (const rel of Object.keys(migrated?.files ?? {})) {
      expect(fs.existsSync(path.join(destRoot, rel))).toBe(true);
    }
  });
});
