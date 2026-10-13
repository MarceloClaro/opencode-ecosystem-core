"""R864: regras reais do Git, contrapróvas e fixtures de reprodução pública."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]

PRIVATE_PATHS = (
    ".opencode/rea/local-assistant/opencode.json",
    ".opencode/rea/local-assistant/mcp-linux.json",
    ".opencode/rea/local-assistant/runtime-state/shared_memory.json",
    ".opencode/rea/local-assistant/evidence/unknown.json",
    ".opencode/rea/evidence/unknown.json",
    ".opencode/browser/runs/private/snapshot.png",
    ".opencode/browser/evidence/private.json",
    ".opencode/scientific-plugins/requests/private.json",
)

UNDECLARED_OUTPUTS = (
    "outputs/private-target.json",
    "outputs/core-r850/native.json",
    "outputs/core-r850/native-stdout.txt",
    "outputs/core-r820/attempt-9/source-manifest-after.json",
    "outputs/core-r853-rx/private-upload.png",
    "outputs/core-r853-rx/repro/backend/private-key.json",
    "livro-core/output/mindmap-slides-R101/slides-livro-core.pptx",
)

ENGINE_FIXTURES = (
    "outputs/core-r842/install-receipt.json",
    "outputs/core-r842/live-evidence.json",
    "outputs/core-r843/config-gates.json",
    "outputs/core-r844/install-receipt.json",
    "outputs/core-r844/live-evidence.json",
    "outputs/core-r852/install-receipt.json",
    "outputs/core-r852/live-evidence.json",
)

RX_FIXTURES = tuple(
    f"outputs/core-r853-rx/{name}"
    for name in (
        "README.md", "rea-evidence.json", "api/health.json", "api/openapi.json",
        "api/pages/docs.html", "api/pages/editor.js", "api/pages/index.html",
        "api/pages/review.html", "api/pages/validacao.html", "repro/backend/app.py",
        "repro/frontend/editor.js", "repro/frontend/index.html",
        "repro/frontend/review.html", "repro/frontend/validacao.html",
    )
)


def ignored(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--quiet", "--", path],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode in (0, 1), result.stderr
    return result.returncode == 0


@pytest.mark.parametrize("path", PRIVATE_PATHS)
def test_estado_privado_fica_fora_do_git(path):
    assert ignored(path) is True, path


@pytest.mark.parametrize("path", UNDECLARED_OUTPUTS)
def test_outputs_nao_declarados_ficam_fora_do_git(path):
    assert ignored(path) is True, path


@pytest.mark.parametrize("path", ENGINE_FIXTURES + RX_FIXTURES)
def test_fixtures_do_contrato_continuam_versionaveis(path):
    assert (ROOT / path).is_file(), path
    assert ignored(path) is False, path


def _linked_receipts() -> set[str]:
    paths = {"outputs/core-r820/attempt-9/full-suite-receipt.json"}
    for name in ("REVISAO_ECOSSISTEMA_R820.md", "REVISAO_REA_R862.md"):
        text = (ROOT / "docs" / name).read_text(encoding="utf-8")
        paths.update(re.findall(r"\]\(\.\./(outputs/[^)#]+)(?:#[^)]*)?\)", text))
    return paths


def test_recibos_publicos_linkados_continuam_versionaveis():
    for path in sorted(_linked_receipts()):
        assert (ROOT / path).is_file(), path
        assert ignored(path) is False, path
        assert (ROOT / path).stat().st_size < 256 * 1024, path


def test_whitelist_nao_libera_diretorios_inteiros():
    public = set(ENGINE_FIXTURES + RX_FIXTURES) | _linked_receipts()
    for directory in sorted({str(Path(path).parent) for path in public}):
        assert ignored(f"{directory}/undeclared-private.json") is True, directory
        assert ignored(f"{directory}/extra-state/record.json") is True, directory
