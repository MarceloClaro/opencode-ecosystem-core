/**
 * remotion-guard.ts — plugin de guarda para Remotion (R1025).
 *
 * Intercepta apenas comandos de shell. Render/still/bundle exigem
 * REMOTION_RENDER_APPROVED=1; instalação exige REMOTION_LICENSE_ACK=1.
 * Prévia (`remotion studio`) e comandos não relacionados passam.
 *
 * O plugin não importa Remotion, não renderiza e não acessa a rede.
 */
import { Plugin } from "@opencode/plugin";
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { decideCommand, validLicenseAck } from "./remotion_policy.mjs";

function licenseAckFromHostFile() {
  try {
    const path = join(homedir(), ".config", "opencode", "remotion-license-ack.json");
    return validLicenseAck(JSON.parse(readFileSync(path, "utf8")));
  } catch {
    return false;
  }
}

export default Plugin.define({
  id: "remotion-guard",
  async setup(ctx) {
    await ctx.tool.hook("execute.before", (event) => {
      const tool = event.tool;
      if (tool !== "shell" && tool !== "bash") return;
      const args = (event.input ?? {}) as Record<string, unknown>;
      const command = args.command;
      if (typeof command !== "string") return;
      const decision = decideCommand(command, {
        renderApproved: process.env.REMOTION_RENDER_APPROVED === "1",
        licenseAck:
          process.env.REMOTION_LICENSE_ACK === "1" || licenseAckFromHostFile(),
      });
      if (decision.decision === "block") {
        throw new Error(`[remotion-guard] ${decision.code}: ${decision.reason}`);
      }
      if (decision.code !== "unrelated") {
        console.log(`[remotion-guard] ${decision.code}: ${decision.command}`);
      }
    });
  },
});
