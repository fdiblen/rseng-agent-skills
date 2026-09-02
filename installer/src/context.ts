import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

/** Shared state every command receives. */
export interface CliContext {
  /** When true, commands report what they would do without writing. */
  dryRun: boolean;
  /** Root directory holding the pack content (skills/, adapters output). */
  packRoot: string;
  log: (message: string) => void;
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
}): CliContext {
  return {
    dryRun: options.dryRun ?? false,
    packRoot: options.packRoot ?? resolvePackRoot(),
    log: options.log ?? ((message) => console.log(message)),
  };
}
