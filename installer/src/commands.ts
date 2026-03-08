import { usableTargets } from "./agents.js";
import { executePlan, planInstall } from "./install.js";
import { registerCommand } from "./program.js";

registerCommand(
  "install",
  "install the pack for detected agents (or the agents given as arguments)",
  (ctx, args) => {
    const wanted = (args.positionals[0] as string[] | undefined) ?? [];
    let targets = usableTargets();
    if (wanted.length > 0) {
      targets = targets.filter((target) => wanted.includes(target.agent));
      if (targets.length === 0) {
        throw new Error(`no matching agent targets for: ${wanted.join(", ")}`);
      }
    }
    for (const target of targets) {
      executePlan(ctx, planInstall(ctx.packRoot, target));
    }
  },
).argument("[agents...]", "restrict to specific agents (claude, copilot, ...)");
