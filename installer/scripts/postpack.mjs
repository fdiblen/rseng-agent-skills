// Remove the staging directory prepack builds.
//
// prepack copies the pack content into installer/content/ so it ships inside
// the tarball. Nothing cleaned it up afterwards, so a single `npm pack` left
// it behind in the checkout, where resolvePackRoot then preferred it over the
// live sources - edits to skills/ stopped having any effect, with no error to
// explain why. Removing it here keeps a packed checkout indistinguishable
// from one that was never packed.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const installerDir = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "..",
);
const contentDir = path.join(installerDir, "content");

if (fs.existsSync(contentDir)) {
  fs.rmSync(contentDir, { recursive: true, force: true });
  console.log("postpack: removed content/");
}
