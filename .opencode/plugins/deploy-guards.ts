/**
 * deploy-guards.ts — Plugin de guards do ecossistema (P0.2/P0.3/P0.4)
 * =====================================================================
 * Conecta os scripts de guarda de `.opencode/hooks/` ao ciclo de vida do
 * OpenCode, com gate FAIL-CLOSED:
 *
 *  - tool.execute.before em `edit`/`write` de `.html` → js_smoke_dom
 *    (stub de DOM em Node; bloqueia a classe de bug R580: 'num' vs '.num').
 *  - tool.execute.before em `bash` contendo `git push`/`git commit` no
 *    repo do site → credential_guard + budget_guard.
 *
 * Segredos: os scripts nunca imprimem o token; plugin só espelha o stdout.
 *
 * @packageDocumentation
 * @module deploy-guards
 */
import type { Plugin } from "@opencode-ai/plugin";
import { execFileSync } from "node:child_process";
import * as path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const HOOKS = path.resolve(HERE, "..", "hooks");

const SITE_REPO_DIR =
  "/home/marceloclaro/opencode-ecosystem-core/research/producao_real/pacote_editorial_podcast_molambudos_gh";

function runHook(script: string, args: string[]): { ok: boolean; out: string } {
  try {
    const out = execFileSync(path.join(HOOKS, script), args, {
      encoding: "utf8",
      timeout: 60_000,
    });
    return { ok: true, out };
  } catch (err: any) {
    return { ok: false, out: String(err?.stderr || err?.message || err) };
  }
}

export default (async () => {
  return {
    "tool.execute.before": async (input: any, output: any) => {
      try {
        const tool = input?.tool as string | undefined;
        const args = output?.args as Record<string, unknown> | undefined;
        if (!tool || !args) return;

        // --- gate js-smoke para edição de HTML ----------------------------
        if ((tool === "edit" || tool === "write") && typeof args.filePath === "string") {
          const fp = args.filePath;
          if (fp.endsWith(".html") || fp.endsWith(".htm")) {
            const r = runHook("js_smoke_dom.sh", [fp]);
            if (!r.ok) {
              throw new Error(
                `[deploy-guards] js-smoke DENIED: ${r.out.trim()}\n` +
                  `Corrija o JS inline (o stub de DOM detecta runtime errors da classe R580).`
              );
            }
            console.log(`[deploy-guards] js-smoke GRANTED: ${fp}`);
          }
        }

        // --- gate credential + budget para push/commit do site -------------
        if (tool === "bash" && typeof args.command === "string") {
          const cmd = args.command;
          if (/git (push|commit)/.test(cmd) && cmd.includes("molambudos-podcast")) {
            const cred = runHook("credential_guard.sh", [SITE_REPO_DIR]);
            if (!cred.ok) {
              throw new Error(`[deploy-guards] credential DENIED: ${cred.out.trim()}`);
            }
            if (/git push/.test(cmd)) {
              const budget = runHook("budget_guard.sh", [SITE_REPO_DIR]);
              if (!budget.ok) {
                throw new Error(`[deploy-guards] budget DENIED: ${budget.out.trim()}`);
              }
            }
            console.log(`[deploy-guards] ${cred.out.trim()}`);
          }
        }
      } catch (err) {
        // fail-closed: propaga o erro para abortar a tool
        throw err;
      }
    },
  };
}) satisfies Plugin;