import assert from "node:assert/strict";
import { decideCommand, validLicenseAck } from "../.opencode/plugins/remotion_policy.mjs";

const cases = [
  ["npx remotion studio --no-open", {}, "allow", "preview_allowed"],
  ["npx remotion compositions", {}, "allow", "remotion_readonly"],
  ["npx remotion render Intro out/video.mp4", {}, "block", "render_requires_approval"],
  ["npx remotion render Intro out/video.mp4", { renderApproved: true }, "allow", "render_approved"],
  ["npx remotion still Intro out/frame.png", {}, "block", "render_requires_approval"],
  ["npx remotion bundle", {}, "block", "render_requires_approval"],
  ["npm install remotion", {}, "block", "license_ack_required"],
  ["npm install remotion", { licenseAck: true }, "allow", "install_license_acknowledged"],
  ["pnpm add @remotion/cli", {}, "block", "license_ack_required"],
  ["ls -la", {}, "allow", "unrelated"],
  ["", {}, "block", "invalid_command"],
];

for (const [command, options, decision, code] of cases) {
  const result = decideCommand(command, options);
  assert.equal(result.decision, decision, `${command}: ${JSON.stringify(result)}`);
  assert.equal(result.code, code, `${command}: ${JSON.stringify(result)}`);
  assert.equal(result.executed, false);
}

assert.equal(validLicenseAck({
  acknowledged: true,
  license: "Remotion License",
  scope: ["install"],
}), true);
assert.equal(validLicenseAck({ acknowledged: true, license: "MIT", scope: ["install"] }), false);
assert.equal(validLicenseAck({ acknowledged: true, license: "Remotion License", scope: ["render"] }), false);
assert.equal(validLicenseAck({ acknowledged: false, license: "Remotion License", scope: ["install"] }), false);
assert.equal(validLicenseAck(null), false);

console.log(JSON.stringify({ ok: true, cases: cases.length }));
