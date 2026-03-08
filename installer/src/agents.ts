import fs from "node:fs";
import os from "node:os";
import path from "node:path";

export type Scope = "project" | "user";

export interface AgentTarget {
  agent: string;
  scope: Scope;
  /** Directory whose presence marks the agent as in use. */
  marker: string;
  /** Where the pack content for this agent is installed. */
  installDir: string;
  detected: boolean;
}

export interface DetectOptions {
  projectDir?: string;
  homeDir?: string;
}

interface AgentSpec {
  agent: string;
  scope: Scope;
  marker: (project: string, home: string) => string;
  installDir: (project: string, home: string) => string;
}

/**
 * Where each supported agent looks for guidance. Project scope drops
 * files into the current repository; user scope into the home directory.
 */
const SPECS: AgentSpec[] = [
  {
    agent: "claude",
    scope: "project",
    marker: (p) => path.join(p, ".claude"),
    installDir: (p) => path.join(p, ".claude", "skills"),
  },
  {
    agent: "claude",
    scope: "user",
    marker: (_p, h) => path.join(h, ".claude"),
    installDir: (_p, h) => path.join(h, ".claude", "skills"),
  },
  {
    agent: "copilot",
    scope: "project",
    marker: (p) => path.join(p, ".github"),
    installDir: (p) => path.join(p, ".github"),
  },
  {
    agent: "cursor",
    scope: "project",
    marker: (p) => path.join(p, ".cursor"),
    installDir: (p) => path.join(p, ".cursor", "rules"),
  },
  {
    agent: "codex",
    scope: "user",
    marker: (_p, h) => path.join(h, ".codex"),
    installDir: (_p, h) => path.join(h, ".codex"),
  },
  {
    agent: "gemini",
    scope: "user",
    marker: (_p, h) => path.join(h, ".gemini"),
    installDir: (_p, h) =>
      path.join(h, ".gemini", "extensions", "rseng-agent-skills"),
  },
];

export function detectAgents(options: DetectOptions = {}): AgentTarget[] {
  const project = options.projectDir ?? process.cwd();
  const home = options.homeDir ?? os.homedir();
  return SPECS.map((spec) => {
    const marker = spec.marker(project, home);
    return {
      agent: spec.agent,
      scope: spec.scope,
      marker,
      installDir: spec.installDir(project, home),
      detected: fs.existsSync(marker),
    };
  });
}

/** The detected targets, or every known target when none is detected. */
export function usableTargets(options: DetectOptions = {}): AgentTarget[] {
  const all = detectAgents(options);
  const detected = all.filter((target) => target.detected);
  return detected.length > 0 ? detected : all;
}
