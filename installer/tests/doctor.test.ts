import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import type { AgentTarget } from "../src/agents.js";
import { diagnose, formatReport } from "../src/doctor.js";
import { executePlan, planInstall } from "../src/install.js";

let packRoot: string;
let destRoot: string;

function write(rel: string, text: string): void {
  const abs = path.join(packRoot, rel);
  fs.mkdirSync(path.dirname(abs), { recursive: true });
  fs.writeFileSync(abs, text);
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
  write("AGENTS.md", "pack umbrella\n");
  write("skills/.keep", "");
  write("package.json", JSON.stringify({ version: "0.1.0" }));
  write("dist/cursor/.cursor/rules/one.mdc", "rule one\n");
  executePlan(
    { dryRun: false, packRoot, log: () => {} },
    planInstall(packRoot, target()),
  );
});

afterEach(() => {
  fs.rmSync(packRoot, { recursive: true, force: true });
  fs.rmSync(destRoot, { recursive: true, force: true });
});

describe("diagnose", () => {
  it("reports a healthy install", () => {
    const report = diagnose(packRoot, target());
    expect(report.installed).toBe(true);
    expect(report.stale).toBe(false);
    expect(report.intact).toEqual([path.join("rules", "one.mdc")]);
    expect(formatReport(report)).toContain("up to date");
  });

  it("reports not installed when there is no manifest", () => {
    const other = { ...target(), installDir: path.join(destRoot, "empty") };
    const report = diagnose(packRoot, other);
    expect(report.installed).toBe(false);
    expect(formatReport(report)).toContain("not installed");
  });

  it("flags user-edited and missing files", () => {
    fs.writeFileSync(path.join(target().installDir, "rules", "one.mdc"), "edited\n");
    let report = diagnose(packRoot, target());
    expect(report.edited).toEqual([path.join("rules", "one.mdc")]);

    fs.rmSync(path.join(target().installDir, "rules", "one.mdc"));
    report = diagnose(packRoot, target());
    expect(report.missing).toEqual([path.join("rules", "one.mdc")]);
    expect(formatReport(report)).toContain("MISSING");
  });

  it("flags staleness against the pack version", () => {
    write("package.json", JSON.stringify({ version: "0.2.0" }));
    const report = diagnose(packRoot, target());
    expect(report.stale).toBe(true);
    expect(formatReport(report)).toContain("STALE");
  });
});
