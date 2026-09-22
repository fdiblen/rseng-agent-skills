// Bundle the pack content into the npm package before packing.
// Copies an explicit whitelist (never a raw directory sweep) from the
// repository into installer/content/, which resolvePackRoot() finds at
// runtime in the published package.
import { execFileSync } from "node:child_process";
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

// Ship only what git tracks. Local working files are kept out of the
// repository through .git/info/exclude, but cpSync never consulted git, so
// four of them sitting under hooks/ were staged for npm while staying
// invisible in `git status` - the one place a release review looks. Refuses
// rather than falling back: a filter that quietly stops filtering is worse
// than no filter, because nobody checks it again.
const GENERATED = new Set(["dist"]);
let tracked;
try {
  tracked = new Set(
    execFileSync("git", ["ls-files", "-z"], { cwd: repoRoot, encoding: "utf8" })
      .split("\0")
      .filter(Boolean),
  );
} catch {
  tracked = null;
}
if (!tracked || tracked.size === 0) {
  console.error(
    "prepack: cannot list git-tracked files, so untracked working files " +
      "cannot be kept out of the tarball; refusing to pack",
  );
  process.exit(1);
}
// A directory is kept when it leads to a tracked file; otherwise an excluded
// one is recreated empty beside the files it was meant to leave out.
const trackedDirs = new Set();
for (const file of tracked) {
  const parts = file.split("/");
  for (let i = 1; i < parts.length; i += 1) {
    trackedDirs.add(parts.slice(0, i).join("/"));
  }
}
const isTracked = (src) => {
  const rel = path.relative(repoRoot, src).split(path.sep).join("/");
  return tracked.has(rel) || trackedDirs.has(rel);
};

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
  // dist/ is exempt: it is generated, deliberately untracked, and is
  // precisely what the package exists to ship.
  const generated = GENERATED.has(entry);
  fs.cpSync(path.join(repoRoot, entry), path.join(contentDir, entry), {
    recursive: true,
    filter: (src) => wanted(src) && (generated || isTracked(src)),
  });
}
// The bundled package.json version is what doctor compares against.
fs.writeFileSync(
  path.join(contentDir, "package.json"),
  JSON.stringify({ version: JSON.parse(fs.readFileSync(path.join(installerDir, "package.json"), "utf8")).version }, null, 2),
);
console.log(`prepack: bundled ${WHITELIST.length} entries into content/`);
