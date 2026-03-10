// Bundle the pack content into the npm package before packing.
// Copies an explicit whitelist (never a raw directory sweep) from the
// repository into installer/content/, which resolvePackRoot() finds at
// runtime in the published package.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const installerDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(installerDir, "..");
const contentDir = path.join(installerDir, "content");

const WHITELIST = ["skills", "dist", "AGENTS.md", "ATTRIBUTION.md", "NOTICE", "LICENSE-content"];

fs.rmSync(contentDir, { recursive: true, force: true });
fs.mkdirSync(contentDir);
for (const entry of WHITELIST) {
  const from = path.join(repoRoot, entry);
  if (!fs.existsSync(from)) {
    console.error(`prepack: missing ${entry}; build adapters first`);
    process.exit(1);
  }
  fs.cpSync(from, path.join(contentDir, entry), { recursive: true });
}
// The bundled package.json version is what doctor compares against.
fs.writeFileSync(
  path.join(contentDir, "package.json"),
  JSON.stringify({ version: JSON.parse(fs.readFileSync(path.join(installerDir, "package.json"), "utf8")).version }, null, 2),
);
console.log(`prepack: bundled ${WHITELIST.length} entries into content/`);
