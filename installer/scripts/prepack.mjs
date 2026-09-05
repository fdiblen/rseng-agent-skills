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

const WHITELIST = ["skills", "commands", "hooks", "agents", "dist", "AGENTS.md", "ATTRIBUTION.md", "NOTICE", "LICENSE", "LICENSE-content"];

// Check everything BEFORE touching the filesystem. These checks used to run
// inside the copy loop, so a failure exited with content/ half-populated -
// and npm does not run postpack when prepack fails, so the staging directory
// stayed behind and shadowed the live sources on the next run.
const newestMtime = (dir) => {
  let newest = 0;
  for (const e of fs.readdirSync(dir, { withFileTypes: true, recursive: true })) {
    if (!e.isFile()) continue;
    newest = Math.max(newest, fs.statSync(path.join(e.parentPath, e.name)).mtimeMs);
  }
  return newest;
};

for (const entry of WHITELIST) {
  if (!fs.existsSync(path.join(repoRoot, entry))) {
    console.error(`prepack: missing ${entry}; build adapters first`);
    process.exit(1);
  }
}
// dist/ is generated. Packing one that predates the sources it came from
// ships stale content, and the failure only shows up for whoever installs
// it. This bit the maintainer during a review: a test ran against a CLI
// forty minutes older than its source and reported a fixed bug as broken.
if (newestMtime(path.join(repoRoot, "dist")) < newestMtime(path.join(repoRoot, "skills"))) {
  console.error(
    "prepack: dist/ is older than skills/ - rebuild the adapters before packing",
  );
  process.exit(1);
}

fs.rmSync(contentDir, { recursive: true, force: true });
fs.mkdirSync(contentDir);
// Never sweep build junk into the tarball. hooks/__pycache__ is gitignored,
// so a .pyc from the packing machine reached npm without git noticing.
const JUNK = new Set(["__pycache__", ".DS_Store", "node_modules", ".pytest_cache"]);
const wanted = (src) => {
  const name = path.basename(src);
  return !JUNK.has(name) && !name.endsWith(".pyc");
};

for (const entry of WHITELIST) {
  fs.cpSync(path.join(repoRoot, entry), path.join(contentDir, entry), {
    recursive: true,
    filter: wanted,
  });
}
// The bundled package.json version is what doctor compares against.
fs.writeFileSync(
  path.join(contentDir, "package.json"),
  JSON.stringify({ version: JSON.parse(fs.readFileSync(path.join(installerDir, "package.json"), "utf8")).version }, null, 2),
);
console.log(`prepack: bundled ${WHITELIST.length} entries into content/`);
