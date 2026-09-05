import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import type { AgentTarget } from "../src/agents.js";
import { confirmTargets, outsideProject } from "../src/commands.js";
import type { CliContext } from "../src/context.js";

function target(installDir: string, agent = "codex"): AgentTarget {
  return {
    agent,
    scope: installDir === process.cwd() ? "project" : "user",
    marker: path.join(installDir, ".codex"),
    installDir,
    detected: true,
  };
}

function ctx(
  answer: boolean,
  dryRun = false,
): CliContext & { asked: string[]; logs: string[] } {
  const asked: string[] = [];
  const logs: string[] = [];
  return {
    dryRun,
    packRoot: "/nowhere",
    log: (m) => logs.push(m),
    confirm: async (q) => {
      asked.push(q);
      return answer;
    },
    asked,
    logs,
  };
}

describe("install confirmation", () => {
  it("does not ask when everything lands in the project", async () => {
    const c = ctx(false);
    expect(await confirmTargets(c, [target(process.cwd())], false)).toBe(true);
    expect(c.asked).toEqual([]);
  });

  it("asks before writing into the home directory", async () => {
    // A bare `install` reaches the home-scoped targets because ~/.codex
    // happens to exist. Two lines of output afterwards is too late.
    const home = path.join(os.homedir(), ".codex");
    const c = ctx(true);
    expect(await confirmTargets(c, [target(home)], false)).toBe(true);
    expect(c.asked).toHaveLength(1);
    expect(c.logs.join("\n")).toContain(home);
  });

  it("aborts when the answer is no", async () => {
    const c = ctx(false);
    expect(
      await confirmTargets(
        c,
        [target(path.join(os.homedir(), ".codex"))],
        false,
      ),
    ).toBe(false);
  });

  it("skips the question for --yes and for a dry run", async () => {
    const home = path.join(os.homedir(), ".codex");
    const yes = ctx(false);
    expect(await confirmTargets(yes, [target(home)], true)).toBe(true);
    expect(yes.asked).toEqual([]);

    const dry = ctx(false, true);
    expect(await confirmTargets(dry, [target(home)], false)).toBe(true);
    expect(dry.asked).toEqual([]);
  });

  it("names only the targets that leave the project", async () => {
    const home = path.join(os.homedir(), ".gemini");
    const outside = outsideProject([
      target(process.cwd(), "cursor"),
      target(home, "gemini"),
    ]);
    expect(outside.map((t) => t.agent)).toEqual(["gemini"]);
  });
});
