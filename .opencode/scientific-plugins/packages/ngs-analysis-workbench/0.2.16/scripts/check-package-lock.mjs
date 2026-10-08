import { readFile } from "node:fs/promises";

const lockfilePath = new URL("../package-lock.json", import.meta.url);
const lockfile = await readFile(lockfilePath, "utf8");
const clusterSocketResolvedUrl =
  /"resolved"\s*:\s*"https:\/\/socket-firewall-registry\.gateway\.[a-z0-9-]+\.internal\.api\.openai\.org\/npm\//g;
const matches = [...lockfile.matchAll(clusterSocketResolvedUrl)];

if (matches.length > 0) {
  const lines = matches.map(
    ({ index }) => lockfile.slice(0, index).split("\n").length,
  );
  console.error(
    `package-lock.json contains ${matches.length} cluster-specific Socket Firewall URL(s) at line(s): ${lines.join(", ")}`,
  );
  console.error(
    "Regenerate it with `npm install --package-lock-only --ignore-scripts`; this project omits registry URLs from lockfiles.",
  );
  process.exit(1);
}
