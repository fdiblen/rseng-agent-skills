import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { buildContext, resolvePackRoot } from "../src/context.js";
import { program, registerCommand } from "../src/program.js";

const REPO_ROOT = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
  "..",
);

describe("context", () => {
  it("resolves the repo checkout as pack root", () => {
    const root = resolvePackRoot(path.join(REPO_ROOT, "installer", "src"));
    expect(root).toBe(REPO_ROOT);
  });

  it("throws when no content is nearby", () => {
    expect(() => resolvePackRoot("/tmp")).toThrow(/cannot locate pack content/);
  });

  it("builds a context with defaults", () => {
    const ctx = buildContext({ packRoot: REPO_ROOT });
    expect(ctx.dryRun).toBe(false);
    expect(ctx.packRoot).toBe(REPO_ROOT);
  });
});

describe("command registration", () => {
  it("passes global dry-run and pack-root into the command context", async () => {
    let seen: { dryRun: boolean; packRoot: string } | undefined;
    registerCommand("probe", "test probe", (ctx) => {
      seen = { dryRun: ctx.dryRun, packRoot: ctx.packRoot };
    });
    await program.parseAsync(
      [
        "node",
        "rseng-agent-skills",
        "--dry-run",
        "--pack-root",
        REPO_ROOT,
        "probe",
      ],
      { from: "node" },
    );
    expect(seen).toEqual({ dryRun: true, packRoot: REPO_ROOT });
  });
});
