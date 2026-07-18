import fs from "node:fs";
import path from "node:path";
import type { AgentTarget } from "./agents.js";
import { readManifest, sha256 } from "./install.js";

export interface DoctorReport {
  target: AgentTarget;
  installed: boolean;
  installedVersion?: string;
  packVersion?: string;
  stale: boolean;
  intact: string[];
  edited: string[];
  missing: string[];
}

function packVersion(packRoot: string): string | undefined {
  const packageJson = path.join(packRoot, "installer", "package.json");
  const bundled = path.join(packRoot, "package.json");
  for (const candidate of [packageJson, bundled]) {
    if (fs.existsSync(candidate)) {
      return JSON.parse(fs.readFileSync(candidate, "utf8")).version;
    }
  }
  return undefined;
}

/** Inspect one agent target's install state without modifying anything. */
export function diagnose(packRoot: string, target: AgentTarget): DoctorReport {
  const manifest = readManifest(target.installDir, target.agent);
  const current = packVersion(packRoot);
  if (!manifest) {
    return {
      target,
      installed: false,
      packVersion: current,
      stale: false,
      intact: [],
      edited: [],
      missing: [],
    };
  }
  const intact: string[] = [];
  const edited: string[] = [];
  const missing: string[] = [];
  for (const [rel, recorded] of Object.entries(manifest.files)) {
    const abs = path.join(target.installDir, rel);
    if (!fs.existsSync(abs)) {
      missing.push(rel);
    } else if (sha256(abs) === recorded) {
      intact.push(rel);
    } else {
      edited.push(rel);
    }
  }
  return {
    target,
    installed: true,
    installedVersion: manifest.version,
    packVersion: current,
    stale: current !== undefined && manifest.version !== current,
    intact,
    edited,
    missing,
  };
}

export function formatReport(report: DoctorReport): string {
  const label = `${report.target.agent} (${report.target.scope})`;
  if (!report.installed) {
    return `${label}: not installed`;
  }
  const parts = [
    `${label}: v${report.installedVersion}`,
    report.stale ? `STALE (pack is v${report.packVersion})` : "up to date",
    `${report.intact.length} intact`,
  ];
  if (report.edited.length > 0) {
    parts.push(
      `${report.edited.length} user-edited (${report.edited.join(", ")})`,
    );
  }
  if (report.missing.length > 0) {
    parts.push(
      `${report.missing.length} MISSING (${report.missing.join(", ")})`,
    );
  }
  return parts.join(", ");
}
