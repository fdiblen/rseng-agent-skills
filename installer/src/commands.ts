import path from "node:path";
import {
  type AgentTarget,
  detectAgents,
  resolveExplicitTargets,
  type Scope,
  usableTargets,
} from "./agents.js";
import type { CliContext } from "./context.js";
import { diagnose, formatReport } from "./doctor.js";
import { executePlan, planInstall, readManifest } from "./install.js";
import { registerCommand } from "./program.js";
import { executeUninstall, planUninstall } from "./uninstall.js";
import { executeUpdate } from "./update.js";

/**
 * Targets that write somewhere other than the current project.
 *
 * Three of the six agents install into the home directory, and a bare
 * `install` reaches them because a `.github/` folder or a `~/.codex`
 * happens to exist. Two lines of output afterwards is not the moment to
 * learn that.
 */
export function outsideProject(targets: AgentTarget[]): AgentTarget[] {
  const project = path.resolve(process.cwd());
  return targets.filter(
    (target) => path.resolve(target.installDir) !== project,
  );
}

export async function confirmTargets(
  ctx: CliContext,
  targets: AgentTarget[],
  assumeYes: boolean,
): Promise<boolean> {
  const outside = outsideProject(targets);
  if (assumeYes || ctx.dryRun || outside.length === 0) {
    return true;
  }
  ctx.log("This will write outside the current project:");
  for (const target of outside) {
    ctx.log(`  ${target.agent} (${target.scope}) -> ${target.installDir}`);
  }
  return ctx.confirm("Continue?");
}

registerCommand(
  "install",
  "install the pack for detected agents (or the agents given as arguments)",
  async (ctx, args) => {
    const wanted = (args.positionals[0] as string[] | undefined) ?? [];
    const scope = args.options["scope"] as Scope | undefined;
    // Naming an agent explicitly forces it even when it is not detected;
    // with no arguments only detected agents are touched. Without --scope
    // an explicit agent resolves to ONE scope (project when the project
    // marker exists, user otherwise); --scope selects the scope directly.
    let targets =
      wanted.length > 0
        ? resolveExplicitTargets(detectAgents(), wanted, scope)
        : usableTargets().filter((target) => target.detected);
    if (wanted.length === 0 && scope) {
      targets = targets.filter((target) => target.scope === scope);
    }
    if (targets.length === 0) {
      throw new Error(
        wanted.length > 0
          ? `no matching agent targets for: ${wanted.join(", ")}${scope ? ` in scope ${scope}` : ""}`
          : "no agents detected; name one explicitly (e.g. install claude)",
      );
    }
    if (!(await confirmTargets(ctx, targets, Boolean(args.options["yes"])))) {
      ctx.log("nothing installed");
      return;
    }
    for (const target of targets) {
      executePlan(ctx, planInstall(ctx.packRoot, target));
    }
  },
)
  .argument("[agents...]", "restrict to specific agents (claude, copilot, ...)")
  .option("--scope <scope>", "limit to project or user scope targets")
  .option("-y, --yes", "do not ask before writing outside the project");

registerCommand(
  "update",
  "update managed files of existing installs, preserving user edits",
  (ctx, args) => {
    const wanted = (args.positionals[0] as string[] | undefined) ?? [];
    const installed = detectAgents().filter(
      (target) =>
        readManifest(target.installDir, target.agent) !== undefined &&
        (wanted.length === 0 || wanted.includes(target.agent)),
    );
    if (installed.length === 0) {
      throw new Error("no existing installs found (no manifest); run install");
    }
    for (const target of installed) {
      executeUpdate(ctx, planInstall(ctx.packRoot, target));
    }
  },
).argument("[agents...]", "restrict to specific agents");

registerCommand(
  "uninstall",
  "remove installed files, leaving anything you have edited in place",
  async (ctx, args) => {
    const wanted = (args.positionals[0] as string[] | undefined) ?? [];
    const plans = detectAgents()
      .filter(
        (target) =>
          readManifest(target.installDir, target.agent) !== undefined &&
          (wanted.length === 0 || wanted.includes(target.agent)),
      )
      .map(planUninstall);
    if (plans.length === 0) {
      throw new Error("no existing installs found (no manifest)");
    }
    const force = Boolean(args.options["force"]);
    if (!ctx.dryRun && !args.options["yes"]) {
      for (const plan of plans) {
        const count = force
          ? plan.managed.length + plan.edited.length
          : plan.managed.length;
        ctx.log(
          `  ${plan.target.agent} (${plan.target.scope}) -> ` +
            `${count} file(s) from ${plan.target.installDir}`,
        );
      }
      if (!(await ctx.confirm("Remove these?"))) {
        ctx.log("nothing removed");
        return;
      }
    }
    for (const plan of plans) {
      executeUninstall(ctx, plan, { force });
    }
  },
)
  .argument("[agents...]", "restrict to specific agents")
  .option("--force", "also remove files you have edited since installing")
  .option("-y, --yes", "do not ask for confirmation");

registerCommand(
  "doctor",
  "check install state per agent: integrity, user edits, staleness",
  (ctx) => {
    for (const target of detectAgents()) {
      ctx.log(formatReport(diagnose(ctx.packRoot, target)));
    }
  },
);
