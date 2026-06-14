import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import {
  detectAgents,
  resolveExplicitTargets,
  usableTargets,
} from "../src/agents.js";

let projectDir: string;
let homeDir: string;

beforeEach(() => {
  projectDir = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-project-"));
  homeDir = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-home-"));
});

afterEach(() => {
  fs.rmSync(projectDir, { recursive: true, force: true });
  fs.rmSync(homeDir, { recursive: true, force: true });
});

describe("detectAgents", () => {
  it("detects nothing in empty directories", () => {
    const targets = detectAgents({ projectDir, homeDir });
    expect(targets.every((t) => !t.detected)).toBe(true);
    expect(targets.map((t) => t.agent)).toContain("claude");
  });

  it("detects project-scoped agents from marker directories", () => {
    fs.mkdirSync(path.join(projectDir, ".github"));
    fs.mkdirSync(path.join(projectDir, ".cursor"));
    const detected = detectAgents({ projectDir, homeDir }).filter(
      (t) => t.detected,
    );
    expect(detected.map((t) => `${t.agent}:${t.scope}`).sort()).toEqual([
      "copilot:project",
      "cursor:project",
    ]);
  });

  it("detects user-scoped agents from home markers", () => {
    fs.mkdirSync(path.join(homeDir, ".claude"));
    fs.mkdirSync(path.join(homeDir, ".gemini"));
    const detected = detectAgents({ projectDir, homeDir }).filter(
      (t) => t.detected,
    );
    expect(detected.map((t) => `${t.agent}:${t.scope}`).sort()).toEqual([
      "claude:user",
      "gemini:user",
    ]);
    const gemini = detected.find((t) => t.agent === "gemini");
    expect(gemini?.installDir).toBe(
      path.join(homeDir, ".gemini", "extensions", "rseng-agent-skills"),
    );
  });

  it("claude installs directly under .claude in both scopes", () => {
    const targets = detectAgents({ projectDir, homeDir }).filter(
      (t) => t.agent === "claude",
    );
    expect(targets.map((t) => t.installDir).sort()).toEqual(
      [path.join(projectDir, ".claude"), path.join(homeDir, ".claude")].sort(),
    );
  });

  it("usableTargets falls back to all targets when none detected", () => {
    expect(usableTargets({ projectDir, homeDir }).length).toBeGreaterThan(4);
    fs.mkdirSync(path.join(projectDir, ".cursor"));
    const usable = usableTargets({ projectDir, homeDir });
    expect(usable).toHaveLength(1);
    expect(usable[0]?.agent).toBe("cursor");
  });
});

describe("resolveExplicitTargets", () => {
  it("prefers project scope when the project marker exists", () => {
    fs.mkdirSync(path.join(projectDir, ".claude"));
    fs.mkdirSync(path.join(homeDir, ".claude"));
    const targets = resolveExplicitTargets(
      detectAgents({ projectDir, homeDir }),
      ["claude"],
    );
    expect(targets.map((t) => `${t.agent}:${t.scope}`)).toEqual([
      "claude:project",
    ]);
  });

  it("falls back to user scope when no project marker exists", () => {
    const targets = resolveExplicitTargets(
      detectAgents({ projectDir, homeDir }),
      ["claude"],
    );
    expect(targets.map((t) => `${t.agent}:${t.scope}`)).toEqual([
      "claude:user",
    ]);
  });

  it("requires --scope user to hit home when a project marker exists", () => {
    fs.mkdirSync(path.join(projectDir, ".claude"));
    const all = detectAgents({ projectDir, homeDir });
    expect(resolveExplicitTargets(all, ["claude"]).map((t) => t.scope)).toEqual(
      ["project"],
    );
    const user = resolveExplicitTargets(all, ["claude"], "user");
    expect(user.map((t) => `${t.agent}:${t.scope}`)).toEqual(["claude:user"]);
  });

  it("keeps the --scope filter behaviour for project scope", () => {
    const targets = resolveExplicitTargets(
      detectAgents({ projectDir, homeDir }),
      ["claude"],
      "project",
    );
    expect(targets.map((t) => `${t.agent}:${t.scope}`)).toEqual([
      "claude:project",
    ]);
  });

  it("leaves single-scope agents untouched", () => {
    const all = detectAgents({ projectDir, homeDir });
    expect(resolveExplicitTargets(all, ["codex"]).map((t) => t.scope)).toEqual([
      "user",
    ]);
    expect(resolveExplicitTargets(all, ["cursor"]).map((t) => t.scope)).toEqual(
      ["project"],
    );
  });
});
