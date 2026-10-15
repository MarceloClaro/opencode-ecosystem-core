# -*- coding: utf-8 -*-
"""Testes dos guards de deploy (SPEC-974 E2/E3/E4) — sem rede, sem efeitos externos.

Cobre o hook `js-smoke` (E3): stub de DOM em Node que converte o bug de runtime
da classe R580 (`'num'` sem ponto → `querySelector` null → TypeError) em falha.

Regressão R900: `SPEC-935-R819-opencode-esm` declarou `"type": "module"` em
`.opencode/package.json` (correto para os plugins/tools), mas o script
`.opencode/hooks/smoke_dom_stub.js` continuava em CommonJS (`require`). Sob o
pacote ESM o Node passou a tratá-lo como módulo ESM e o load crashava com
`ReferenceError: require is not defined`, fazendo o gate negar *toda* edição de
`.html`. Estes testes travam o aceite da E3 de forma automática.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
OPENCODE = ROOT / ".opencode"
STUB = OPENCODE / "hooks" / "smoke_dom_stub.js"
SH = OPENCODE / "hooks" / "js_smoke_dom.sh"
PKG = OPENCODE / "package.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="Node.js é necessário para o hook js-smoke")


GOOD_HTML = """<!doctype html><html><body>
<div class="card num">x</div>
<script>
var el = document.querySelector('.num');
el.textContent = 'ok';
</script>
</body></html>
"""

# Classe R580: seletor 'num' (sem ponto) não existe no DOM → null → TypeError.
BAD_HTML = """<!doctype html><html><body>
<div class="card num">x</div>
<script>
var el = document.querySelector('num');
el.textContent = 'boom';
</script>
</body></html>
"""


def _run_stub(html_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [NODE, str(STUB), str(html_path)],
        capture_output=True,
        text=True,
        cwd=str(ROOT),  # mesmo cwd do plugin (execFileSync sem cwd explícito)
    )


def test_stub_carrega_e_aprova_html_correto(tmp_path: Path):
    """Pré-fix isto crashava no load (ESM/CJS) e retornava exit 1."""
    good = tmp_path / "good.html"
    good.write_text(GOOD_HTML, encoding="utf-8")
    r = _run_stub(good)
    assert r.returncode == 0, (r.stdout, r.stderr)
    assert "SMOKE_OK" in r.stdout
    assert "require is not defined" not in r.stderr


def test_stub_detecta_bug_r580(tmp_path: Path):
    bad = tmp_path / "bad.html"
    bad.write_text(BAD_HTML, encoding="utf-8")
    r = _run_stub(bad)
    assert r.returncode != 0, (r.stdout, r.stderr)
    assert "SMOKE_FAIL" in (r.stdout + r.stderr)


def test_wrapper_bash_granted_e_denied(tmp_path: Path):
    good = tmp_path / "good.html"
    good.write_text(GOOD_HTML, encoding="utf-8")
    bad = tmp_path / "bad.html"
    bad.write_text(BAD_HTML, encoding="utf-8")

    ok = subprocess.run([str(SH), str(good)], capture_output=True, text=True, cwd=str(ROOT))
    assert ok.returncode == 0, (ok.stdout, ok.stderr)
    assert "GRANTED" in ok.stdout

    denied = subprocess.run([str(SH), str(bad)], capture_output=True, text=True, cwd=str(ROOT))
    assert denied.returncode != 0, (denied.stdout, denied.stderr)


def test_nenhum_js_commonjs_sob_pacote_esm():
    """R819 declarou ESM; nenhum `.js` de `.opencode/` pode usar `require` cru.

    Este é o teste-guarda que faltava e deixou o `smoke_dom_stub.js` quebrado.
    """
    if not PKG.exists():
        pytest.skip(".opencode/package.json ausente")
    pkg = json.loads(PKG.read_text(encoding="utf-8"))
    if pkg.get("type") != "module":
        pytest.skip(".opencode não declara type=module")

    infratores = []
    for js in OPENCODE.rglob("*.js"):
        if "node_modules" in js.parts:
            continue
        txt = js.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(txt.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            if "require(" in line and not stripped.startswith("//"):
                infratores.append(f"{js.relative_to(ROOT)}:{i}: {stripped}")

    assert infratores == [], (
        "Sob .opencode/package.json (type=module), arquivos .js devem usar "
        "import (ESM), não require (CommonJS). Infratores:\n" + "\n".join(infratores)
    )
