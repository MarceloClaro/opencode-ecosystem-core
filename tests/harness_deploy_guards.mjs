/**
 * Harness de verificação do plugin deploy-guards.ts (SPEC-935-R900 / SPEC-935-R1004).
 *
 * Importa o plugin REAL (caminho via env PLUGIN_PATH) e invoca o hook
 * `execute.before` registrado via `ctx.tool.hook` — o contrato da API V2.
 * Prova que a validação usa o CONTEÚDO PROSPECTIVO (a versão que será gravada)
 * e não o arquivo em disco nem o caminho.
 *
 * Execução: PLUGIN_PATH=... node --experimental-strip-types harness_deploy_guards.mjs
 * Exige Node >= 22.6 (type stripping nativo).
 */
const PLUGIN =
  process.env.PLUGIN_PATH ||
  "/home/marceloclaro/opencode-ecosystem-core/.opencode/plugins/deploy-guards.ts";
const TMP = "/tmp/opencode/harness";

import * as fs from "node:fs";

const mod = await import(PLUGIN);
const definition = mod.default;

if (typeof definition !== "object" || definition === null || typeof definition.setup !== "function") {
  throw new Error(`plugin não exporta definição V2 {id, setup}: ${typeof definition}`);
}

let before = null;
const registered = [];
await definition.setup({
  tool: {
    hook: async (name, callback) => {
      registered.push(name);
      if (name === "execute.before") before = callback;
      return { dispose: async () => {} };
    },
  },
});

if (typeof before !== "function") {
  throw new Error(`hook execute.before não registrado (hooks: ${registered.join(", ")})`);
}

const CLEAN = `<!doctype html><html><body><div class="card num">x</div>
<script>var el=document.querySelector('.num');el.textContent='ok';</script>
</body></html>`;

const BUGGY = `<!doctype html><html><body><div class="card num">x</div>
<script>var el=document.querySelector('num');el.textContent='ok';</script>
</body></html>`;

fs.mkdirSync(TMP, { recursive: true });
let pass = 0, fail = 0;

async function probe(label, input, output, expectDenied) {
  let denied = false, msg = "";
  try {
    await before({ tool: input.tool, input: output.args });
  } catch (err) {
    denied = true;
    msg = String(err?.message || err);
  }
  const ok = denied === expectDenied;
  ok ? pass++ : fail++;
  console.log(
    `${ok ? "PASS" : "FAIL"}  ${label}\n` +
      `      esperado=${expectDenied ? "DENIED" : "GRANTED"} obtido=${denied ? "DENIED" : "GRANTED"}` +
      (denied ? `\n      msg: ${msg.split("\n")[0]}` : "")
  );
}

const NEW = "/tmp/opencode/harness/nao-existe-ainda.html";
try { fs.unlinkSync(NEW); } catch {}

// 1) write de arquivo NOVO com JS limpo -> GRANTED (antes: DENIED por ENOENT)
await probe(
  "write novo .html, JS limpo  (antes negava ENOENT)",
  { tool: "write" },
  { args: { path: NEW, content: CLEAN } },
  false
);

// 2) write de arquivo NOVO com bug R580 -> DENIED
await probe(
  "write novo .html, bug R580 (querySelector('num'))",
  { tool: "write" },
  { args: { path: NEW, content: BUGGY } },
  true
);

// 3) edit que CORRIGE um arquivo em disco: disco=BUGGY, edit aplicaria CLEAN
//    -> GRANTED (validar o disco defasado negaria o BOM)
const alvo = `${TMP}/alvo.html`;
fs.writeFileSync(alvo, BUGGY, "utf8");
await probe(
  "edit que corrige arquivo em disco (disco=buggy -> prospectivo=clean)",
  { tool: "edit" },
  { args: { path: alvo, oldString: "querySelector('num')", newString: "querySelector('.num')" } },
  false
);

// 4) edit que INTRODUZ bug R580 -> DENIED
await probe(
  "edit que introduz bug R580 (disco=clean -> prospectivo=buggy)",
  { tool: "edit" },
  { args: { path: alvo, oldString: "querySelector('.num')", newString: "querySelector('num')" } },
  true
);

// 5) write sem 'content' (indeterminável) -> não nega (skip)
await probe(
  "write sem 'content' (conteúdo indeterminável -> não nega)",
  { tool: "write" },
  { args: { path: NEW } },
  false
);

console.log(`\nRESUMO: ${pass} passaram, ${fail} falharam`);
process.exit(fail === 0 ? 0 : 1);
