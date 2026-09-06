import fs from "node:fs";
import path from "node:path";
import readline from "node:readline/promises";
import { fileURLToPath } from "node:url";

/** Shared state every command receives. */
export interface CliContext {
  /** When true, commands report what they would do without writing. */
  dryRun: boolean;
  /** Root directory holding the pack content (skills/, adapters output). */
  packRoot: string;
  log: (message: string) => void;
  /**
   * Ask before doing something the user may not have pictured. Returns
   * true without asking when there is nobody to ask - a CI run must not
   * block on a prompt nobody will ever see.
   */
  confirm: (question: string) => Promise<boolean>;
}

/**
 * Read a yes/no answer from the terminal.
 *
 * Answers on a non-TTY stdin: an install piped through a script has no
 * one at the keyboard, and a prompt there is a hang rather than a
 * question. Callers that must not proceed unattended check
 * `process.stdin.isTTY` themselves.
 */
export async function askTerminal(question: string): Promise<boolean> {
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    // Say so rather than passing silently. A devcontainer build or a CI
    // step cannot answer, so the run continues - but a safety question
    // that quietly answers itself stops meaning anything.
    console.log(
      "Not a terminal, so continuing without asking. Use --dry-run to preview.",
    );
    return true;
  }
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  try {
    const answer = await rl.question(`${question} [y/N] `);
    return /^y(es)?$/i.test(answer.trim());
  } finally {
    rl.close();
  }
}

/**
 * Locate the pack content root. In the published npm package the content
 * is bundled under content/ next to dist/; in a repository checkout the
 * repo root itself is the content root (skills/ lives there).
 */
export function resolvePackRoot(moduleDir?: string): string {
  const here = moduleDir ?? path.dirname(fileURLToPath(import.meta.url));
  // In a checkout the live sources win over any bundled snapshot. prepack
  // writes content/ and nothing used to remove it, so after a single
  // `npm pack` the snapshot shadowed the repo and edits to skills/ silently
  // stopped taking effect. A sibling src/ exists only in a checkout, never
  // in the published package, which is the honest way to tell them apart.
  const inCheckout = fs.existsSync(path.resolve(here, "..", "src"));
  const bundled = path.resolve(here, "..", "content");
  const checkout = path.resolve(here, "..", "..");
  const candidates = inCheckout ? [checkout, bundled] : [bundled, checkout];
  for (const candidate of candidates) {
    if (
      fs.existsSync(path.join(candidate, "AGENTS.md")) &&
      fs.existsSync(path.join(candidate, "skills"))
    ) {
      return candidate;
    }
  }
  throw new Error(
    "cannot locate pack content (no AGENTS.md + skills/ near the CLI)",
  );
}

export function buildContext(options: {
  dryRun?: boolean;
  packRoot?: string;
  log?: (message: string) => void;
  confirm?: (question: string) => Promise<boolean>;
}): CliContext {
  return {
    dryRun: options.dryRun ?? false,
    packRoot: options.packRoot ?? resolvePackRoot(),
    log: options.log ?? ((message) => console.log(message)),
    confirm: options.confirm ?? askTerminal,
  };
}
