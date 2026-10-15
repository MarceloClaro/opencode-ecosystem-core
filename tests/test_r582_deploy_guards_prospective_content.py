"""Regressão do gate js-smoke do plugin deploy-guards (SPEC-935-R900).

História do defeito (dois bugs em cadeia):
  1. `smoke_dom_stub.js` era CommonJS sob `.opencode/package.json` com
     `"type":"module"` → `ReferenceError: require is not defined in ES module
     scope` → o guard negava QUALQUER edição .html.
  2. Mesmo com o stub corrigido, o plugin validava o arquivo já em disco via
     `runHook("js_smoke_dom.sh", [fp])`. Consequências:
        - `write` de arquivo NOVO era negado com `ENOENT` (arquivo não existe).
        - `edit` testava a VERSÃO ANTIGA e não a que seria gravada (um edit
          corretivo era negado; um edit que introduzia o bug passava).

A correção introduce `prospectiveContent()` (write → `args.content`; edit →
aplica `oldString`→`newString` sobre o disco) e `smokeGate()` (valida esse
conteúdo num arquivo temporário; `null` → SKIPPED sem falso bloqueio).

Este teste trava o comportamento no plugin REAL (não numa cópia), invocando
a função de hook `tool.execute.before` como o host faria.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / ".opencode" / "plugins" / "deploy-guards.ts"
HARNESS = Path(__file__).resolve().parent / "harness_deploy_guards.mjs"


def _node_version() -> tuple[int, int]:
    """Versão do Node (type stripping exige >= 22.6)."""
    node = shutil.which("node")
    if node is None:
        return (0, 0)
    try:
        out = subprocess.run(
            [node, "-v"], capture_output=True, text=True, timeout=30
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return (0, 0)
    m = re.match(r"v(\d+)\.(\d+)", out)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


@pytest.fixture(scope="module")
def plugin_source() -> str:
    assert PLUGIN.is_file(), f"plugin ausente: {PLUGIN}"
    return PLUGIN.read_text(encoding="utf-8")


def test_plugin_defina_conteudo_prospectivo(plugin_source: str) -> None:
    """RED: a versão antiga não tinha `prospectiveContent`/`smokeGate`."""
    assert "function prospectiveContent" in plugin_source
    assert "function smokeGate" in plugin_source


def test_hook_valida_o_conteudo_prospectivo_e_nao_o_caminho(plugin_source: str) -> None:
    """O hook deve validar o conteúdo a gravar, nunca o caminho cru.

    O padrão antigo `runHook("js_smoke_dom.sh", [fp])` é exatamente o bug do
    ENOENT em `write` de arquivo novo.
    """
    assert "prospectiveContent(tool, args)" in plugin_source
    assert "smokeGate(content, fp)" in plugin_source
    assert 'runHook("js_smoke_dom.sh", [fp])' not in plugin_source, (
        "regressão: guard voltou a validar o caminho em vez do conteúdo"
    )


def test_hook_e_fail_closed_nao_engole_erro(plugin_source: str) -> None:
    """Degradação: o catch relança para abortar a tool (fail-closed)."""
    assert "throw err" in plugin_source


@pytest.mark.skipif(
    _node_version() < (22, 6),
    reason="exige Node >= 22.6 (type stripping nativo de .ts)",
)
def test_comportamento_do_hook_real(plugin_source: str) -> None:
    """Cinco casos comportamentais executados contra o plugin real.

    1. write novo, JS limpo          → GRANTED (era DENIED/ENOENT)
    2. write novo, bug R580          → DENIED com SMOKE_FAIL
    3. edit que corrige o disco      → GRANTED (validar o disco negaria o BOM)
    4. edit que introduz o bug       → DENIED
    5. write sem `content`           → SKIPPED (sem falso bloqueio)
    """
    assert HARNESS.is_file(), f"harness ausente: {HARNESS}"
    env = dict(os.environ, PLUGIN_PATH=str(PLUGIN))
    proc = subprocess.run(
        ["node", "--experimental-strip-types", str(HARNESS)],
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
        cwd=str(REPO),
    )
    combinado = f"{proc.stdout}\n{proc.stderr}"
    # O stub Node emite ExperimentalWarning em stderr; ignoramos o aviso.
    assert proc.returncode == 0, f"harness falhou:\n{combinado}"
    assert "RESUMO: 5 passaram, 0 falharam" in proc.stdout
    # Cada caso comportamental deve estar explícito no relatório.
    for marcador in (
        "write novo .html, JS limpo",
        "bug R580 (querySelector('num'))",
        "edit que corrige arquivo em disco",
        "edit que introduz bug R580",
        "write sem 'content'",
    ):
        assert marcador in proc.stdout, f"caso ausente do relatório: {marcador}"
    assert "DENIED" in proc.stdout and "GRANTED" in proc.stdout
    # O bug original precisa aparecer negado com SMOKE_FAIL real, não ENOENT.
    assert "SMOKE_FAIL" in proc.stdout
    # Nenhum DENIED pode ser causado por ENOENT (bug antigo do caminho):
    # qualquer DENIED deve vir do stub do DOM (SMOKE_FAIL).
    for linha in proc.stdout.splitlines():
        if "DENIED" in linha:
            assert "ENOENT" not in linha, f"DENIED por ENOENT (regressão): {linha!r}"
