"""R1084: deny-by-default no livro e inventário público reproduzível."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]
LIT = "literatura/molambudos"


def _ignored(path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--quiet", "--no-index", path],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode in (0, 1), result.stderr
    return result.returncode == 0


@pytest.mark.parametrize(
    "path",
    [
        f"{LIT}/private/.env",
        f"{LIT}/private/.env.production",
        f"{LIT}/private/prod.key",
        f"{LIT}/private/secret.pem",
        f"{LIT}/private/credentials.json:Zone.Identifier",
        f"{LIT}/private/sessao.xlsx",
        f"{LIT}/private/credentials.json",
        f"{LIT}/private/api-token.txt.bak",
        f"{LIT}/book/main.xdv",
        f"{LIT}/book/main.synctex(busy)",
        f"{LIT}/book/main_kdp_print_160x230mm.pdf",
        f"{LIT}/capas/molambudos_final/outra_capa_nao_aprovada.pdf",
        f"{LIT}/podcast/producao/pacote_editorial_podcast_molambudos_gh/README.md",
        "literatura/academicos/01_dissertacao_opencode",
    ],
)
def test_literature_secrets_artifacts_and_external_links_stay_ignored(path):
    assert _ignored(path), path


@pytest.mark.parametrize(
    "path",
    [
        f"{LIT}/README.md",
        f"{LIT}/Molambudos_Print_R1077/main.tex",
        f"{LIT}/capas/molambudos_final/molambudos_capa_completa_422p_print_300dpi.pdf",
        f"{LIT}/capas/molambudos_final/molambudos_capa_completa_436p_canonica_300dpi.pdf",
        f"{LIT}/capas/molambudos_final/422p_print/capa_frontal_160x230mm_300dpi.png",
    ],
)
def test_documented_sources_and_selected_covers_are_allowed(path):
    assert not _ignored(path), path


def test_build_residue_removed_from_index_and_ignored_in_clean_clone():
    for name in (
        "literatura/livros/ia-odontologia/template/main.xdv",
        f"{LIT}/Molambudos_VictoriaRegia/tri/main_kdp_print_160x230mm.synctex(busy)",
    ):
        # Um clone não possui estes arquivos locais (não exigir sua presença).
        assert _ignored(name)
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", name],
            cwd=ROOT, check=False, capture_output=True,
        )
        assert result.returncode != 0, name


def test_no_external_symlinks_or_huge_files_are_tracked_under_literature():
    result = subprocess.run(
        ["git", "ls-files", "-s", "-z", "--", "literatura"],
        cwd=ROOT, check=True, capture_output=True,
    )
    for entry in result.stdout.split(b"\0"):
        if not entry:
            continue
        mode, path = entry.split(b"\t", 1)
        assert not mode.startswith(b"120000 "), path  # symlink Git
        source = ROOT / path.decode("utf-8", "surrogateescape")
        if source.is_file():
            assert source.stat().st_size < 100_000_000, source


def test_badges_match_current_config_and_have_reconciler_markers():
    config = json.loads((ROOT / "opencode.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for key, label in (("agent", "agents"), ("mcp", "MCP")):
        assert f"badge/{label}-{len(config[key])}" in readme
    assert readme.count("<!-- core-badges:start -->") == 1
    assert readme.count("<!-- core-badges:end -->") == 1


def test_readme_explains_git_clone_boundaries_and_page_variants():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "435 pp" in readme and "422 pp" in readme and "436 pp" in readme
    assert "lombada" in readme and "confirm" in readme
    assert "clone" in readme.lower()
    assert "Git LFS" in readme
    assert "9.552 testes coletados" not in readme


def test_linked_repository_guide_does_not_forbid_approved_literary_sources():
    text = (ROOT / "docs/REPOSITORIO_REPRODUZIVEL.md").read_text(encoding="utf-8")
    assert "Manuscritos, dados de pesquisas paralelas" not in text
    assert "literatura/" in text and "SPEC-935-R1084" in text


def test_whitespace_gate_is_not_disabled_for_python_and_docs():
    for path in ("README.md", "scripts/reconcile_operational_docs.py"):
        result = subprocess.run(
            ["git", "check-attr", "whitespace", "--", path],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        assert "-trailing-space" not in result.stdout
    result = subprocess.run(
        ["git", "check-attr", "text", "eol", "--", "install.sh"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    assert "text: set" in result.stdout and "eol: lf" in result.stdout
