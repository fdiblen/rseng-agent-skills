import { Command } from "commander";
import { type CliContext, buildContext } from "./context.js";

export type CommandAction = (
  ctx: CliContext,
  args: Record<string, unknown>,
) => Promise<void> | void;

export const program = new Command()
  .name("rseng-agent-skills")
  .description(
    "Install research software quality skills from RSQKit (EVERSE project) into AI coding agents",
  )
  .version("0.1.0")
  .option("--dry-run", "report planned changes without writing anything")
  .option("--pack-root <dir>", "override the pack content root (development)");

/**
 * Register a subcommand that receives the shared CLI context. The global
 * --dry-run and --pack-root options are resolved here so individual
 * commands never re-implement them.
 */
export function registerCommand(
  name: string,
  description: string,
  action: CommandAction,
): Command {
  return program
    .command(name)
    .description(description)
    .action(async (args: Record<string, unknown>, command: Command) => {
      const globals = command.parent?.opts() ?? {};
      const ctx = buildContext({
        dryRun: Boolean(globals["dryRun"]),
        packRoot: globals["packRoot"] as string | undefined,
      });
      await action(ctx, args);
    });
}
