import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { afterEach, beforeEach, describe, expect, it } from "vitest";

// These tests RUN prepack.mjs. They used to regex-match its source text,
// which meant they could only fail when the wording changed - a rewrite that
// swapped cpSync's arguments, or moved a guard to after the copy, passed
// untouched. Both of those were real defects.

const SCRIPT = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "scripts",
  "prepack.mjs",
);

const WHITELIST = [
  "skills",
  "commands",
  "hooks",
  "agents",
  "dist",
  "AGENTS.md",
  "ATTRIBUTION.md",
  "NOTICE",
  "LICENSE",
  "LICENSE-content",
];

let root: string;
let installer: string;

/** A miniature repository laid out the way prepack expects. */
function makeRepo(): void {
  root = fs.mkdtempSync(path.join(os.tmpdir(), "rseng-prepack-"));
  installer = path.join(root, "installer");
  fs.mkdirSync(path.join(installer, "scripts"), { recursive: true });
  fs.copyFileSync(SCRIPT, path.join(installer, "scripts", "prepack.mjs"));
  fs.writeFileSync(
    path.join(installer, "package.json"),
    JSON.stringify({ name: "x", version: "9.9.9" }),
  );
  for (const entry of WHITELIST) {
    const target = path.join(root, entry);
    if (entry.includes(".")) {
      fs.writeFileSync(target, `${entry}\n`);
    } else {
      fs.mkdirSync(path.join(target, "inner"), { recursive: true });
      fs.writeFileSync(path.join(target, "inner", "file.md"), `${entry}\n`);
    }
  }
  // dist/ must look newer than skills/ or the freshness guard fires.
  const later = Date.now() / 1000 + 60;
  fs.utimesSync(path.join(root, "dist", "inner", "file.md"), later, later);
}

function runPrepack(): { status: number; output: string } {
  try {
    const out = execFileSync(
      "node",
      [path.join(installer, "scripts", "prepack.mjs")],
      { cwd: installer, encoding: "utf8", stdio: "pipe" },
    );
    return { status: 0, output: out };
  } catch (error) {
    const e = error as { status?: number; stderr?: string; stdout?: string };
    return {
      status: e.status ?? 1,
      output: `${e.stdout ?? ""}${e.stderr ?? ""}`,
    };
  }
}

beforeEach(makeRepo);
afterEach(() => fs.rmSync(root, { recursive: true, force: true }));

describe("prepack", () => {
  it("stages exactly the whitelisted entries and nothing else", () => {
    expect(runPrepack().status).toBe(0);
    const staged = fs.readdirSync(path.join(installer, "content")).sort();
    expect(staged).toEqual([...WHITELIST, "package.json"].sort());
  });

  it("does not sweep in build junk", () => {
    // hooks/__pycache__ is gitignored, so a .pyc from the packing machine
    // reached npm without git ever noticing.
    const cache = path.join(root, "hooks", "__pycache__");
    fs.mkdirSync(cache, { recursive: true });
    fs.writeFileSync(path.join(cache, "phase_lib.cpython-313.pyc"), "junk");
    fs.writeFileSync(path.join(root, "skills", ".DS_Store"), "junk");

    expect(runPrepack().status).toBe(0);
    const staged = execFileSync(
      "find",
      [path.join(installer, "content"), "-type", "f"],
      { encoding: "utf8" },
    );
    expect(staged).not.toMatch(/__pycache__|\.pyc|\.DS_Store/);
  });

  it("records the installer's real version for doctor to compare against", () => {
    runPrepack();
    const bundled = JSON.parse(
      fs.readFileSync(path.join(installer, "content", "package.json"), "utf8"),
    );
    expect(bundled.version).toBe("9.9.9");
  });

  it("refuses to pack when a whitelist entry is missing", () => {
    fs.rmSync(path.join(root, "agents"), { recursive: true });
    const result = runPrepack();
    expect(result.status).toBe(1);
    expect(result.output).toContain("agents");
  });

  it("refuses to pack a dist older than the skills it came from", () => {
    const stale = Date.now() / 1000 - 3600;
    for (const f of fs.readdirSync(path.join(root, "dist", "inner"))) {
      fs.utimesSync(path.join(root, "dist", "inner", f), stale, stale);
    }
    expect(runPrepack().status).toBe(1);
  });

  it("leaves no staging directory behind when it refuses", () => {
    // npm does not run postpack when prepack fails, so a half-populated
    // content/ used to survive and then shadow the live sources.
    fs.rmSync(path.join(root, "agents"), { recursive: true });
    runPrepack();
    expect(fs.existsSync(path.join(installer, "content"))).toBe(false);
  });
});
