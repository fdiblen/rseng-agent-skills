import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";

const SCRIPT = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "scripts",
  "prepack.mjs",
);

function readWhitelist(): string[] {
  const source = fs.readFileSync(SCRIPT, "utf8");
  const match = source.match(/const WHITELIST = \[([^\]]*)\]/);
  if (!match?.[1]) {
    throw new Error("prepack.mjs no longer declares a WHITELIST array");
  }
  return match[1]
    .split(",")
    .map((entry) => entry.trim().replace(/^"|"$/g, ""))
    .filter((entry) => entry.length > 0);
}

describe("prepack whitelist", () => {
  it("stays an explicit list including the claude pack content", () => {
    const whitelist = readWhitelist();
    expect(whitelist).toEqual([
      "skills",
      "commands",
      "agents",
      "dist",
      "AGENTS.md",
      "ATTRIBUTION.md",
      "NOTICE",
      "LICENSE-content",
    ]);
  });

  it("only bundles entries from the whitelist (no directory sweep)", () => {
    const source = fs.readFileSync(SCRIPT, "utf8");
    // The only cpSync call must iterate WHITELIST entries, never the
    // repository root wholesale.
    expect(source).toContain("for (const entry of WHITELIST)");
    expect(source.match(/cpSync/g)).toHaveLength(1);
  });

  it("every committed whitelist entry exists in the repository", () => {
    const repoRoot = path.resolve(path.dirname(SCRIPT), "..", "..");
    for (const entry of readWhitelist()) {
      // dist/ is the adapter build output: generated, gitignored, and absent
      // from a fresh clone until the pipeline has run.
      if (entry === "dist") continue;
      expect(fs.existsSync(path.join(repoRoot, entry)), entry).toBe(true);
    }
  });

  it("refuses to pack when a whitelist entry is missing", () => {
    const source = fs.readFileSync(SCRIPT, "utf8");
    expect(source).toContain("if (!fs.existsSync(from))");
    expect(source).toContain("process.exit(1)");
  });
});
