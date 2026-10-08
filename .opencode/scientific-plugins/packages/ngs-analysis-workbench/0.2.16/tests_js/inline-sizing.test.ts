import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

test("inline receipts override the shared document minimum after base styles", () => {
  const entrypoint = readFileSync(new URL("../src/inline-main.tsx", import.meta.url), "utf8");
  const inlineStyles = readFileSync(new URL("../src/styles/inline.css", import.meta.url), "utf8");

  assert.ok(entrypoint.indexOf('"./styles/base.css"') < entrypoint.indexOf('"./styles/inline.css"'));
  assert.match(inlineStyles, /html,\s*body,\s*#root\s*\{\s*min-height:\s*0\s*;/);
});
