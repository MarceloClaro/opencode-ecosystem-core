"""SPEC-979 — Agente + Skill + Plugin + MCP (paridade OA/fechado, sem rede)."""
from pathlib import Path
import json
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_r979_agent_checkbox():
    p = Path("agents/catalog/54_agente_acesso_aberto_auditoria_fichamento.md")
    assert p.exists()
    t = p.read_text(encoding="utf-8")
    for k in ("name:", "description:", "Missao", "Nunca Faca", "Sci-Hub", "auditoria"):
        assert k in t, k


def test_r979_skill_checkbox():
    p = Path(".opencode/skills/acesso-aberto-auditoria/SKILL.md")
    assert p.exists()
    t = p.read_text(encoding="utf-8")
    assert "disable-model-invocation: true" in t
    assert "criar_pasta_auditoria" in t and "auditar_pasta" in t


def test_r979_plugin_checkbox():
    p = Path(".opencode/plugins/acesso-aberto-auditoria.ts")
    assert p.exists()
    t = p.read_text(encoding="utf-8")
    assert "Plugin" in t and "acesso-aberto-auditoria" in t and "unauthorized_source" in t


def test_r979_mcp_tools():
    from integrations.acesso_aberto_auditoria_mcp import mcp
    tools = None
    for attr in ("_tools", "_tool_handlers", "tools"):
        if hasattr(mcp, attr):
            tools = getattr(mcp, attr)
            break
    # Fallback: importa funções decoradas diretamente
    import integrations.acesso_aberto_auditoria_mcp as mod
    for fn in ("resolver_doi", "verificar_oa", "criar_pasta_auditoria", "adicionar_recorte", "auditar_pasta"):
        assert hasattr(mod, fn), fn


def test_r979_paridade(tmp_path):
    from research.auditoria_fichamento import criar_pasta_auditoria, auditar_pasta
    base = str(tmp_path)
    oa = {"doi": "10.1371/journal.pone.0024352", "titulo": "OA", "autores": ["Silva, J"],
          "ano": 2011, "fonte": "openalex", "licenca": "cc-by", "pdf_url": "https://exemplo.org/oa.pdf"}
    p1 = criar_pasta_auditoria(base, oa, pdf_bytes=b"%PDF-1.4 oa", runner_allowed=lambda m: {"allowed": True})
    assert (Path(p1) / "artigo.pdf").exists()
    fech = {"doi": "10.1038/nature12373", "titulo": "Fech", "autores": ["A"], "ano": 2013}
    p2 = criar_pasta_auditoria(base, fech, pdf_bytes=b"%PDF-1.4 x", runner_allowed=lambda m: {"allowed": False})
    assert not (Path(p2) / "artigo.pdf").exists()
    assert auditar_pasta(p1, [])["aprovado"] is True


def _execute_real_plugin(payload, *, mode="execute"):
    """Importa o SDK/plugin reais e bloqueia efeitos externos durante a prova."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node é necessário para executar o plugin OpenCode real.")
    script = r"""
import fs from 'node:fs';
import http from 'node:http';
import https from 'node:https';
import {syncBuiltinESMExports} from 'node:module';
const payload = JSON.parse(fs.readFileSync(0, 'utf8'));
let networkCalls = 0, fileWrites = 0;
const forbiddenNetwork = () => { networkCalls++; throw new Error('unexpected_network'); };
const forbiddenWrite = () => { fileWrites++; throw new Error('unexpected_file_creation'); };
globalThis.fetch = forbiddenNetwork;
http.request = http.get = https.request = https.get = forbiddenNetwork;
for (const name of ['writeFile', 'writeFileSync', 'appendFile', 'appendFileSync', 'mkdir', 'mkdirSync']) fs[name] = forbiddenWrite;
for (const name of ['writeFile', 'appendFile', 'mkdir']) fs.promises[name] = forbiddenWrite;
syncBuiltinESMExports();
try {
  const {default: factory} = await import(process.argv[1]);
  const {tool} = await import(process.argv[2]);
  const hooks = await factory({});
  const operation = hooks.tool['acesso-aberto-auditoria'];
  if (process.argv[3] === 'json-schema') {
    const schema = tool.schema.toJSONSchema(tool.schema.object(operation.args).strict());
    console.log(JSON.stringify({ok: true, schema, networkCalls, fileWrites}));
  } else if (process.argv[3] === 'schema') {
    const parsed = tool.schema.object(operation.args).strict().safeParse(payload);
    console.log(JSON.stringify({ok: parsed.success, parsed: parsed.success ? parsed.data : null, networkCalls, fileWrites}));
  } else {
    const result = await operation.execute(payload, {});
    console.log(JSON.stringify({ok: true, result_type: typeof result, output: typeof result === 'string' ? JSON.parse(result) : result, networkCalls, fileWrites}));
  }
} catch (error) {
  console.log(JSON.stringify({ok: false, error: String(error), networkCalls, fileWrites}));
}
"""
    process = subprocess.run(
        [node, "--experimental-strip-types", "--input-type=module", "-e", script,
         (ROOT / ".opencode/plugins/acesso-aberto-auditoria.ts").as_uri(),
         (ROOT / ".opencode/node_modules/@opencode-ai/plugin/dist/index.js").as_uri(), mode],
        input=json.dumps(payload), cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert process.returncode == 0, process.stderr[-1500:]
    report = json.loads(process.stdout)
    assert report["networkCalls"] == 0
    assert report["fileWrites"] == 0
    return report


def test_r979_real_plugin_uses_sdk_zod_arguments():
    report = _execute_real_plugin({"doi": "10.1371/journal.pone.0024352"}, mode="schema")
    assert report["ok"] is True
    assert report["parsed"]["doi"] == "10.1371/journal.pone.0024352"


def test_r979_real_plugin_schema_can_be_published_to_provider():
    report = _execute_real_plugin({}, mode="json-schema")
    assert report["ok"] is True, report
    assert report["schema"]["properties"]["doi"]["type"] == "string"
    assert report["schema"]["properties"]["pdfUrl"]["type"] == "string"
    assert report["schema"]["required"] == ["doi"]
    assert report["schema"]["additionalProperties"] is False


@pytest.mark.parametrize("doi", [
    "10.1371/journal.pone.0024352", " DOI: 10.1371/JOURNAL.PONE.0024352 ",
    "https://doi.org/10.1371/JOURNAL.PONE.0024352",
    "HTTP://DX.DOI.ORG/10.1371/JOURNAL.PONE.0024352",
])
def test_r979_real_plugin_returns_canonical_serialized_guidance(doi):
    report = _execute_real_plugin({"doi": doi})
    assert report["ok"] is True
    assert report["result_type"] == "string"
    result = report["output"]
    assert result["doi"] == "10.1371/journal.pone.0024352"
    assert result["pasta"] == "auditoria_fichamentos/10-1371-journal-pone-0024352"
    assert result["guidance_only"] is True
    assert result["file_creation"] is False
    assert result["pipeline_executed"] is False
    assert result["network_performed"] is False
    assert result["evidence_eligible"] is False
    assert result["revisaoHumanaObrigatoria"] is True


@pytest.mark.parametrize("payload", [
    None, [], {}, {"doi": False}, {"doi": 1234}, {"doi": ["10.1371/x"]},
    {"doi": "10.1371/x", "unexpected": True},
    {"doi": "10.1371/x 10.1038/y"}, {"doi": ""},
    {"doi": "10.1371/x", "pdfUrl": False},
    {"doi": "10.1371/x", "pdfUrl": 0},
    {"doi": "10.1371/x", "pdfUrl": ""},
    {"doi": "10.1371/x", "pdfUrl": "not a URL"},
    {"doi": "10.1371/x", "pdfUrl": "file:///tmp/article.pdf"},
])
def test_r979_real_plugin_refuses_whole_invalid_input(payload):
    assert _execute_real_plugin(payload)["ok"] is False
    assert _execute_real_plugin(payload, mode="schema")["ok"] is False


@pytest.mark.parametrize("url", [
    "https://SCI-HUB.example/article", "https://example.org/ScIhUb/file.pdf",
    "scihub-mcp://archive/article", "https://example.org/?source=SCI-HUB",
])
def test_r979_real_plugin_blocks_source_case_insensitively(url):
    report = _execute_real_plugin({"doi": "10.1371/x", "pdfUrl": url})
    assert report["ok"] is False
    assert "unauthorized_source" in report["error"]


def test_r979_real_plugin_candidate_url_is_guidance_only():
    report = _execute_real_plugin({"doi": "10.1371/x", "pdfUrl": "https://example.org/article.pdf"})
    assert report["ok"] is True
    assert report["result_type"] == "string"
    assert report["output"]["guidance_only"] is True
    assert report["output"]["file_creation"] is False
