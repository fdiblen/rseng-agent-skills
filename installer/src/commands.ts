import { detectAgents, usableTargets } from "./agents.js";
import { executePlan, planInstall } from "./install.js";
import { registerCommand } from "./program.js";

registerCommand(
  "install",
  "install the pack for detected agents (or the agents given as arguments)",
  (ctx, args) => {
    const wanted = (args.positionals[0] as string[] | undefined) ?? [];
    // Naming an agent explicitly forces it even when it is not detected;
    // with no arguments only detected agents are touched.
    const targets =
      wanted.length > 0
        ? detectAgents().filter((target) => wanted.includes(target.agent))
        : usableTargets().filter((target) => target.detected);
    if (targets.length === 0) {
      throw new Error(
        wanted.length > 0
          ? `unknown agent(s): ${wanted.join(", ")}`
          : "no agents detected; name one explicitly (e.g. install claude)",
      );
    }
    for (const target of targets) {
      executePlan(ctx, planInstall(ctx.packRoot, target));
    }
  },
).argument("[agents...]", "restrict to specific agents (claude, copilot, ...)");
