import { Command } from "commander";
import { buildContext, type CliContext, resolvePackRoot } from "./context.js";
import { packVersion } from "./install.js";

function cliVersion(): string {
  try {
    return packVersion(resolvePackRoot()) ?? "unknown";
  } catch {
    return "unknown";
  }
}

export interface CommandArgs {
  /** Positional arguments in declaration order. */
  positionals: unknown[];
  /** Option values for this subcommand. */
  options: Record<string, unknown>;
}

export type CommandAction = (
  ctx: CliContext,
  args: CommandArgs,
) => Promise<void> | void;

export const program = new Command()
  .name("rseng-agent-skills")
  .description(
    "Install research software engineering practice skills, into AI coding agents",
  )
  // Read it rather than repeat it: the same drift the install manifest
  // had, where a literal outlived the release it named. Guarded because
  // resolvePackRoot throws when the content is missing, and --version
  // should still answer.
  .version(cliVersion())
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
    .action(async (...invocation: unknown[]) => {
      const command = invocation.at(-1) as Command;
      const options = invocation.at(-2) as Record<string, unknown>;
      const globals = command.parent?.opts() ?? {};
      const ctx = buildContext({
        dryRun: Boolean(globals["dryRun"]),
        packRoot: globals["packRoot"] as string | undefined,
      });
      await action(ctx, { positionals: invocation.slice(0, -2), options });
    });
}
