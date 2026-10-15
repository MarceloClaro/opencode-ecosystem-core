/**
 * Harness de verificação do plugin deploy-guards.ts (SPEC-935-R900).
 *
 * Importa o plugin REAL (caminho via env PLUGIN_PATH) e invoca a função de
 * hook `tool.execute.before` com payloads simulados, provando que a
 * validação usa o CONTEÚDO PROSPECTIVO (a versão que será gravada) e não o
 * arquivo em disco nem o caminho.
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
const plugin = await mod.default(); // export default é uma factory async
const before = plugin["tool.execute.before"];

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
    await before(input, output);
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
  { args: { filePath: NEW, content: CLEAN } },
  false
);

// 2) write de arquivo NOVO com bug R580 -> DENIED
await probe(
  "write novo .html, bug R580 (querySelector('num'))",
  { tool: "write" },
  { args: { filePath: NEW, content: BUGGY } },
  true
);

// 3) edit que CORRIGE um arquivo em disco: disco=BUGGY, edit aplicaria CLEAN
//    -> GRANTED (validar o disco defasado negaria o BOM)
const alvo = `${TMP}/alvo.html`;
fs.writeFileSync(alvo, BUGGY, "utf8");
await probe(
  "edit que corrige arquivo em disco (disco=buggy -> prospectivo=clean)",
  { tool: "edit" },
  { args: { filePath: alvo, oldString: "querySelector('num')", newString: "querySelector('.num')" } },
  false
);

// 4) edit que INTRODUZ bug R580 -> DENIED
await probe(
  "edit que introduz bug R580 (disco=clean -> prospectivo=buggy)",
  { tool: "edit" },
  { args: { filePath: alvo, oldString: "querySelector('.num')", newString: "querySelector('num')" } },
  true
);

// 5) write sem 'content' (indeterminável) -> não nega (skip)
await probe(
  "write sem 'content' (conteúdo indeterminável -> não nega)",
  { tool: "write" },
  { args: { filePath: NEW } },
  false
);

console.log(`\nRESUMO: ${pass} passaram, ${fail} falharam`);
process.exit(fail === 0 ? 0 : 1);
