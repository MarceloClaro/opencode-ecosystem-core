/**
 * deploy-guards.ts — Plugin de guards do ecossistema (P0.2/P0.3/P0.4)
 * =====================================================================
 * Conecta os scripts de guarda de `.opencode/hooks/` ao ciclo de vida do
 * OpenCode, com gate FAIL-CLOSED.
 *
 * API V2 (SPEC-935-R1004): o host exige `export default { id, setup }` e
 * registra hooks por domínio — `ctx.tool.hook("execute.before", …)`. O mapa
 * `"tool.execute.before"` da V1 nunca é executado pela V2, o que deixava o
 * gate silenciosamente inerte.
 *
 *  - `edit`/`write` de `.html` → js_smoke_dom
 *    (stub de DOM em Node; bloqueia a classe de bug R580: 'num' vs '.num').
 *  - `shell` (ou `bash` na V1) com `git push`/`git commit` no repo do site
 *    → credential_guard + budget_guard.
 *
 * Nomes de campo: a V2 usa `path`; a V1 usava `filePath`. O guard aceita os
 * dois — usar apenas um deles tornaria o gate inerte sob o outro runtime.
 *
 * Correção R900: o gate de smoke valida o CONTEÚDO PROSPECTIVO (o que será
 * gravado), não o arquivo em disco. Um `write` de `.html` novo não pode ser
 * negado por ENOENT e um `edit` não pode validar a versão ANTIGA.
 *
 * Segredos: os scripts nunca imprimem o token; plugin só espelha o stdout.
 *
 * @packageDocumentation
 * @module deploy-guards
 */
import { Plugin } from "@opencode/plugin";
import { execFileSync } from "node:child_process";
import * as fs from "node:fs";
import * as os from "node:os";
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

/** Caminho do alvo: `path` (V2) ou `filePath` (V1). */
function argumentPath(args: Record<string, unknown>): string | undefined {
  const candidate = args.path ?? args.filePath;
  return typeof candidate === "string" ? candidate : undefined;
}

/**
 * Reconstrói o conteúdo que a tool está prestes a gravar.
 * - `write`: usa `args.content`.
 * - `edit`: aplica `oldString`→`newString` (com `replaceAll`) sobre o disco.
 * Retorna `null` quando o conteúdo prospectivo não é determinável.
 */
function prospectiveContent(tool: string, args: Record<string, unknown>): string | null {
  if (tool === "write") {
    return typeof args.content === "string" ? args.content : null;
  }
  // edit
  const fp = argumentPath(args);
  const oldString = args.oldString;
  const newString = args.newString;
  if (typeof fp !== "string" || typeof oldString !== "string" || typeof newString !== "string") {
    return null;
  }
  let current: string;
  try {
    current = fs.readFileSync(fp, "utf8");
  } catch {
    return null; // arquivo inexistente: não é possível validar
  }
  const all = args.replaceAll === true;
  return all ? current.split(oldString).join(newString) : current.replace(oldString, newString);
}

/** Roda o stub de DOM sobre conteúdo em arquivo temporário. Fail-closed. */
function smokeGate(content: string, label: string): void {
  const tmp = path.join(
    os.tmpdir(),
    `js-smoke-${process.pid}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}.html`
  );
  try {
    fs.writeFileSync(tmp, content, "utf8");
    const r = runHook("js_smoke_dom.sh", [tmp]);
    if (!r.ok) {
      throw new Error(
        `[deploy-guards] js-smoke DENIED: ${r.out.trim()}\n` +
          `Corrija o JS inline (o stub de DOM detecta runtime errors da classe R580).`
      );
    }
    console.log(`[deploy-guards] js-smoke GRANTED: ${label}`);
  } finally {
    try {
      fs.unlinkSync(tmp);
    } catch {
      /* melhor esforço */
    }
  }
}

export default Plugin.define({
  id: "deploy-guards",
  async setup(ctx) {
    await ctx.tool.hook("execute.before", (event) => {
      try {
        const tool = event.tool;
        const args = (event.input ?? {}) as Record<string, unknown>;
        if (!tool) return;

        // --- gate js-smoke para edição de HTML ----------------------------
        if (tool === "edit" || tool === "write") {
          const fp = argumentPath(args);
          if (fp && (fp.endsWith(".html") || fp.endsWith(".htm"))) {
            const content = prospectiveContent(tool, args);
            if (content === null) {
              // Conteúdo prospectivo não determinável: não há o que validar.
              // Não negar (evita falso fail-closed); registrar para auditoria.
              console.log(`[deploy-guards] js-smoke SKIPPED (conteúdo indeterminável): ${fp}`);
            } else {
              smokeGate(content, fp);
            }
          }
        }

        // --- lacuna conhecida: `patch` grava múltiplos arquivos ------------
        // O conteúdo não é reconstruível sem interpretar o patch; auditar em
        // vez de negar, para não introduzir falso fail-closed.
        if (tool === "patch" && typeof args.patchText === "string" && /\.html?\b/.test(args.patchText)) {
          console.log("[deploy-guards] js-smoke SKIPPED (tool patch com .html): valide manualmente");
        }

        // --- gate credential + budget para push/commit do site -------------
        if ((tool === "shell" || tool === "bash") && typeof args.command === "string") {
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
    });
  },
});
