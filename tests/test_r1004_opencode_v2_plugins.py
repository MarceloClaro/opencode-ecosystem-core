# -*- coding: utf-8 -*-
"""SPEC-935-R1004 — contrato de plugins do OpenCode V2.

História do defeito: o runtime `@opencode/cli@2.2.5` rejeitou os três plugins
locais porque o export default era uma FUNÇÃO (API V1). O carregador V2 exige
um objeto `{ id, effect|setup }` e nunca executa implementações V1:

    PluginModule.LoadError: Plugin must export a default definition with an id
    and an effect or setup function. (SchemaError: Expected object at ["default"])

Os testes antigos (R979/R582/R210) chamavam `mod.default()` como factory V1,
portanto ficavam verdes enquanto o host rejeitava o plugin. Este arquivo trava
o contrato real e o comportamento observável dos callbacks registrados.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / ".opencode" / "plugins"
HARNESS = Path(__file__).with_name("harness_v2_plugins.mjs")
PKG = ROOT / ".opencode" / "package.json"

ACESSO = PLUGINS / "acesso-aberto-auditoria.ts"
DEPLOY = PLUGINS / "deploy-guards.ts"
LITERT = PLUGINS / "litert-lm-provider.ts"

NODE = shutil.which("node")


def _node_version() -> tuple[int, int]:
    if NODE is None:
        return (0, 0)
    try:
        out = subprocess.run([NODE, "-v"], capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return (0, 0)
    m = re.match(r"v(\d+)\.(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


pytestmark = pytest.mark.skipif(
    NODE is None or _node_version() < (22, 6),
    reason="exige Node >= 22.6 (type stripping nativo de .ts)",
)


def _run(plugin: Path, mode: str) -> dict:
    proc = subprocess.run(
        [NODE, "--experimental-strip-types", str(HARNESS), str(plugin), mode],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=str(ROOT),
    )
    combinado = f"{proc.stdout}\n{proc.stderr}"
    assert proc.returncode == 0, combinado[-2000:]
    line = [ln for ln in proc.stdout.strip().splitlines() if ln.startswith("{")]
    assert line, f"harness não emitiu JSON:\n{combinado[-2000:]}"
    return json.loads(line[-1])


# ── CA1/CA2/CA3 — contrato do carregador e ausência de V1 ────────────────────


@pytest.mark.parametrize("plugin", [ACESSO, DEPLOY, LITERT], ids=lambda p: p.name)
def test_cada_plugin_exporta_definicao_v2(plugin: Path) -> None:
    assert plugin.is_file(), f"plugin ausente: {plugin}"
    report = _run(plugin, "contract")
    assert report["ok"] is True, report
    shape = report["shape"]
    assert shape["isObject"] is True, f"default deve ser objeto, não {type(shape)}"
    assert shape["isFunction"] is False
    assert isinstance(shape["id"], str) and shape["id"]
    assert shape["hasSetup"] or shape["hasEffect"]


def _codigo_sem_comentarios(src: str) -> str:
    """Remove comentários para checar USO da API, não a menção histórica."""
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    return "\n".join(linha for linha in src.splitlines() if not linha.lstrip().startswith("//"))


def test_plugins_nao_usam_api_v1() -> None:
    for plugin in (ACESSO, DEPLOY, LITERT):
        src = _codigo_sem_comentarios(plugin.read_text(encoding="utf-8"))
        assert "@opencode-ai/plugin" not in src, f"{plugin.name} ainda importa o SDK V1"
        assert '"tool.execute.before"' not in src, f"{plugin.name} ainda registra hook V1"
        assert "export default (async" not in src, f"{plugin.name} ainda exporta factory V1"


def test_dependencia_v2_declarada() -> None:
    pkg = json.loads(PKG.read_text(encoding="utf-8"))
    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
    assert "@opencode/plugin" in deps, "declarar @opencode/plugin em .opencode/package.json"
    assert deps["@opencode/plugin"].startswith("2."), deps["@opencode/plugin"]


# ── CA4..CA7 — ferramenta de acesso aberto ───────────────────────────────────


def test_acesso_registra_ferramenta_com_json_schema() -> None:
    report = _run(ACESSO, "acesso")
    assert report["ok"] is True, report
    assert report["tool"]["hasInputSchema"] is True
    assert "doi" in (report["tool"]["required"] or [])


def test_acesso_orienta_doi_valido() -> None:
    report = _run(ACESSO, "acesso")
    case = next(c for c in report["cases"] if c["label"] == "doi simples")
    assert case["threw"] is False, case
    out = case["parsed"]
    assert out["doi"] == "10.1371/journal.pone.0024352"
    assert out["guidance_only"] is True
    assert out["network_performed"] is False
    assert out["file_creation"] is False
    assert out["pipeline_executed"] is False
    assert out["evidence_eligible"] is False
    assert out["revisaoHumanaObrigatoria"] is True
    assert out["pasta"].startswith("auditoria_fichamentos/")


def test_acesso_recusa_doi_invalido() -> None:
    report = _run(ACESSO, "acesso")
    case = next(c for c in report["cases"] if c["label"] == "doi invalido")
    assert case["threw"] is True


def test_acesso_bloqueia_fonte_nao_autorizada() -> None:
    report = _run(ACESSO, "acesso")
    sci = next(c for c in report["cases"] if c["label"] == "sci-hub bloqueado")
    assert sci["threw"] is True
    assert "unauthorized_source" in sci["message"]
    ftp = next(c for c in report["cases"] if c["label"] == "esquema nao http")
    assert ftp["threw"] is True


# ── CA8..CA10 — guard de deploy ──────────────────────────────────────────────


def test_deploy_registra_hook_execute_before() -> None:
    report = _run(DEPLOY, "deploy")
    assert report.get("ok") is True, report
    assert len(report["cases"]) >= 6


def test_deploy_nega_write_html_com_bug_r580() -> None:
    report = _run(DEPLOY, "deploy")
    case = next(c for c in report["cases"] if c["label"] == "write V2 (path) bug R580")
    assert case["threw"] is True, case
    assert "SMOKE_FAIL" in case["message"] or "DENIED" in case["message"]


def test_deploy_aprova_write_html_limpo() -> None:
    report = _run(DEPLOY, "deploy")
    for label in ("write V2 (path) html limpo", "edit V2 corrige o disco"):
        case = next(c for c in report["cases"] if c["label"] == label)
        assert case["threw"] is False, case


def test_deploy_le_campos_v1_e_v2() -> None:
    """O host V2 usa `path`; aceitar `filePath` evita guard silenciosamente inerte."""
    report = _run(DEPLOY, "deploy")
    v1 = next(c for c in report["cases"] if c["label"] == "compat V1 (filePath) bug R580")
    assert v1["threw"] is True, v1


# ── CA11..CA12 — provider LiteRT-LM ──────────────────────────────────────────


def test_litert_registra_provider_sem_duplicar() -> None:
    report = _run(LITERT, "litert")
    assert report["ok"] is True, report
    assert any(e["op"] == "add" for e in report["empty"])
    assert not any(e["op"] == "add" for e in report["existing"])


def test_litert_preserva_modelos_obrigatorios() -> None:
    src = LITERT.read_text(encoding="utf-8")
    for model_id in (
        "litert-community/gemma-4-E4B-it-litert-lm",
        "litert-community/gemma-4-12B-it-litert-lm",
        "litert-community/gemma-4-E2B-it-litert-lm",
        "litert-community/Qwen3-0.6B",
    ):
        assert model_id in src, f"modelo {model_id} ausente"
    report = _run(LITERT, "litert")
    add = next(e for e in report["empty"] if e["op"] == "add")
    assert add["models"] == 4
