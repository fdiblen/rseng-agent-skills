import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import type { AgentTarget } from "../src/agents.js";
import type { CliContext } from "../src/context.js";
import {
  BACKUPS_KEPT,
  executePlan,
  planInstall,
  pruneBackups,
  readManifest,
} from "../src/install.js";
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
  write("dist/cursor/.cursor/rules/one.mdc", "rule one v1\n");
  write("dist/cursor/.cursor/rules/two.mdc", "rule two v1\n");
  write("dist/cursor/.agents/skills/rseng-testing/SKILL.md", "skill v1\n");
  // The notices travel with CC-BY content, so planInstall requires them.
  write("dist/cursor/ATTRIBUTION.md", "credit\n");
  write("dist/cursor/NOTICE", "credit\n");
  write("dist/cursor/LICENSE-content", "credit\n");
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
    // 3 content files plus the three CC-BY notices that ship beside them.
    expect(result.updated).toBe(6);
    expect(result.preserved).toEqual([]);
    const updated = fs.readFileSync(
      path.join(target().installDir, ".cursor", "rules", "one.mdc"),
      "utf8",
    );
    expect(updated).toBe("rule one v2\n");
  });

  it("preserves user-edited files and reports them", () => {
    const edited = path.join(
      target().installDir,
      ".cursor",
      "rules",
      "two.mdc",
    );
    fs.writeFileSync(edited, "my local customization\n");
    write("dist/cursor/.cursor/rules/two.mdc", "rule two v2\n");

    const result = executeUpdate(ctx(), planInstall(packRoot, target()));
    expect(result.preserved).toEqual([
      path.join(".cursor", "rules", "two.mdc"),
    ]);
    expect(fs.readFileSync(edited, "utf8")).toBe("my local customization\n");
    // The preserved file's manifest hash now matches its edited content,
    // so a second update still leaves it alone.
    const again = executeUpdate(ctx(), planInstall(packRoot, target()));
    expect(again.preserved).toEqual([path.join(".cursor", "rules", "two.mdc")]);
  });

  it("backs up managed files before replacing", () => {
    write("dist/cursor/.cursor/rules/one.mdc", "rule one v2\n");
    const result = executeUpdate(ctx(), planInstall(packRoot, target()));
    expect(result.backupDir).toBeDefined();
    const backup = fs.readFileSync(
      path.join(result.backupDir as string, ".cursor", "rules", "one.mdc"),
      "utf8",
    );
    expect(backup).toBe("rule one v1\n");
  });

  it("dry-run reports without touching anything", () => {
    write("dist/cursor/.cursor/rules/one.mdc", "rule one v2\n");
    executeUpdate(ctx(true), planInstall(packRoot, target()));
    const current = fs.readFileSync(
      path.join(target().installDir, ".cursor", "rules", "one.mdc"),
      "utf8",
    );
    expect(current).toBe("rule one v1\n");
    expect(logs.some((l) => l.includes("[dry-run]"))).toBe(true);
  });

  it("refuses to update without a manifest", () => {
    fs.rmSync(
      path.join(target().installDir, ".rseng-agent-skills.cursor.json"),
    );
    expect(() => executeUpdate(ctx(), planInstall(packRoot, target()))).toThrow(
      /run install first/,
    );
    expect(readManifest(target().installDir, "cursor")).toBeUndefined();
  });
});

describe("retired files", () => {
  it("removes files the new release no longer ships", () => {
    // A renamed skill file used to stay on disk while dropping out of the
    // manifest: untracked forever, and invisible to doctor.
    executePlan(ctx(), planInstall(packRoot, target()));
    const gone = path.join(target().installDir, ".cursor", "rules", "two.mdc");
    expect(fs.existsSync(gone)).toBe(true);

    fs.rmSync(path.join(packRoot, "dist/cursor/.cursor/rules/two.mdc"));
    write("dist/cursor/.cursor/rules/renamed.mdc", "rule two v2\n");

    const result = executeUpdate(ctx(), planInstall(packRoot, target()));
    expect(result.removed).toEqual([path.join(".cursor", "rules", "two.mdc")]);
    expect(fs.existsSync(gone)).toBe(false);
    expect(
      Object.keys(readManifest(target().installDir, "cursor")?.files ?? {}),
    ).toContain(path.join(".cursor", "rules", "renamed.mdc"));
  });

  it("keeps a retired file the user has edited", () => {
    executePlan(ctx(), planInstall(packRoot, target()));
    const kept = path.join(target().installDir, ".cursor", "rules", "two.mdc");
    fs.writeFileSync(kept, "my own notes\n");

    fs.rmSync(path.join(packRoot, "dist/cursor/.cursor/rules/two.mdc"));
    const result = executeUpdate(ctx(), planInstall(packRoot, target()));

    expect(result.removed).toEqual([]);
    expect(fs.readFileSync(kept, "utf8")).toBe("my own notes\n");
  });
});

describe("backup retention", () => {
  it("keeps only the newest few and reports what it removed", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-prune-"));
    // Older than the keep window, and deliberately out of name order so the
    // test proves the sort is on mtime rather than on the random suffix.
    const made: string[] = [];
    for (let i = 0; i < BACKUPS_KEPT + 3; i += 1) {
      const d = path.join(dir, `.rseng-backup-${String(i).padStart(2, "0")}`);
      fs.mkdirSync(d);
      fs.writeFileSync(path.join(d, "kept.txt"), "x");
      fs.utimesSync(d, 1_000 + i, 1_000 + i);
      made.push(d);
    }
    const other = path.join(dir, "not-a-backup");
    fs.mkdirSync(other);

    const removed = pruneBackups(dir);

    expect(removed).toBe(3);
    const left = fs
      .readdirSync(dir)
      .filter((n) => n.startsWith(".rseng-backup-"))
      .sort();
    expect(left.length).toBe(BACKUPS_KEPT);
    // The survivors are the most recently touched ones.
    expect(left).toEqual(
      made
        .slice(-BACKUPS_KEPT)
        .map((d) => path.basename(d))
        .sort(),
    );
    expect(fs.existsSync(other)).toBe(true);
  });

  it("does nothing when the directory has no backups", () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-prune-"));
    expect(pruneBackups(dir)).toBe(0);
  });
});
