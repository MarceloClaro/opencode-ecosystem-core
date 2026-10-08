import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

import { build } from "vite";

const root = fileURLToPath(new URL("../", import.meta.url));
const manifest = await readFile(new URL("../../../manage/blob_data.hashes", import.meta.url), "utf8");
const hashes = new Map(
  [...manifest.matchAll(/\[\[file\]\]\s+name = "([^"]+)"\s+hash = "([a-f0-9]{64})"/g)]
    .map((match) => [match[1], match[2]]),
);
const mismatches = [];

// Rebuild in memory: a cached HTML file can agree with the release manifest
// while both still implement an obsolete MCP response contract.
for (const [config, filename] of [
  ["vite.config.ts", "mcp-app.html"],
  ["vite.inline.config.ts", "mcp-inline.html"],
]) {
  const name = `plugins/ngs-analysis-workbench/mcp/${filename}`;
  const expected = hashes.get(name);
  assert.ok(expected, `Missing release hash for ${name}`);
  const result = await build({ root, configFile: `${root}${config}`, build: { write: false } });
  const outputs = Array.isArray(result) ? result : [result];
  const html = outputs.flatMap((output) => output.output)
    .find((output) => output.type === "asset" && output.fileName === filename);
  assert.ok(html, `Build did not produce ${filename}`);
  const actual = createHash("sha256").update(html.source).digest("hex");
  if (actual !== expected) {
    mismatches.push(`${name}: source build ${actual}, released blob ${expected}`);
  }
}

assert.equal(
  mismatches.length,
  0,
  `NGS App release assets are stale. Rebuild and upload the App assets before releasing.\n${mismatches.join("\n")}`,
);
console.log("Both NGS App release hashes match fresh source builds.");
