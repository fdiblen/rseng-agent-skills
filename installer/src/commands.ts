import {
  detectAgents,
  resolveExplicitTargets,
  type Scope,
  usableTargets,
} from "./agents.js";
import { diagnose, formatReport } from "./doctor.js";
import { executePlan, planInstall, readManifest } from "./install.js";
import { registerCommand } from "./program.js";
import { executeUpdate } from "./update.js";

registerCommand(
  "install",
  "install the pack for detected agents (or the agents given as arguments)",
  (ctx, args) => {
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
    for (const target of targets) {
      executePlan(ctx, planInstall(ctx.packRoot, target));
    }
  },
)
  .argument("[agents...]", "restrict to specific agents (claude, copilot, ...)")
  .option("--scope <scope>", "limit to project or user scope targets");

registerCommand(
  "update",
  "update managed files of existing installs, preserving user edits",
  (ctx, args) => {
    const wanted = (args.positionals[0] as string[] | undefined) ?? [];
    const installed = detectAgents().filter(
      (target) =>
        readManifest(target.installDir) !== undefined &&
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
  "doctor",
  "check install state per agent: integrity, user edits, staleness",
  (ctx) => {
    for (const target of detectAgents()) {
      ctx.log(formatReport(diagnose(ctx.packRoot, target)));
    }
  },
);
