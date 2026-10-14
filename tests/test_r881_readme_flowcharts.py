"""Contratos R881: sincronização integral dos fluxogramas no README."""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/sync_readme_flowcharts.py"
START = "<!-- core-flowcharts:start -->"
END = "<!-- core-flowcharts:end -->"
ANCHOR = "## Limites de segurança e operação"


def run_sync(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True, text=True, timeout=30, check=False,
    )


@pytest.fixture
def sample_root(tmp_path: Path) -> Path:
    flows = tmp_path / "docs/architecture/flows"
    flows.mkdir(parents=True)
    (tmp_path / "src").mkdir()
    (tmp_path / "src/core.py").write_text("def start():\n    return 1\n", encoding="utf-8")
    entries = []
    for number, name, code in (
        (1, "Entrada íntegra", 'flowchart TB\n  A["Entrada"] --> B{"Aceitar?"}\n  B -->|"não"| C["Recusar"]\n'),
        (2, "Saída íntegra", 'flowchart LR\n  X["Dado"] -. "composição" .-> Y["Saída"]\n'),
    ):
        filename = f"flows/{number:02d}-sample.mmd"
        (flows / Path(filename).name).write_text(code, encoding="utf-8")
        (flows / Path(filename).with_suffix(".svg").name).write_text("<svg/>", encoding="utf-8")
        entries.append({
            "id": f"sample-{number}", "title": name,
            "description": f"Descrição completa {number}.", "file": filename,
            "sources": [{"path": "src/core.py", "symbol": "start", "line": 1}],
            "limitations": [f"Limitação integral {number}."],
        })
    (tmp_path / "docs/architecture/flows.json").write_text(
        json.dumps({"version": 1, "flows": entries}, ensure_ascii=False), encoding="utf-8",
    )
    (tmp_path / "README.md").write_bytes(
        b"# Documento\r\n\r\nConteudo anterior.\r\n\r\n"
        + ANCHOR.encode() + b"\r\n\r\nConteudo posterior.\r\n"
    )
    return tmp_path


def test_catalogo_real_todos_13_integralmente_publicados_no_readme():
    """Omitir um fluxo, uma aresta ou metadado do catálogo rompe o contrato."""
    catalog = json.loads((ROOT / "docs/architecture/flows.json").read_text(encoding="utf-8"))
    assert len(catalog["flows"]) == 13
    result = run_sync(ROOT, "--check")
    assert result.returncode == 0, result.stdout + result.stderr
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert text.count(START) == text.count(END) == 1
    block = text.split(START, 1)[1].split(END, 1)[0]
    assert re.findall(r"^### \d+\. (.+)$", block, re.MULTILINE) == [
        entry["title"] for entry in catalog["flows"]
    ]
    diagrams = re.findall(r"```mermaid\n(.*?)```", block, re.DOTALL)
    assert len(diagrams) == 13
    assert diagrams == [
        (ROOT / "docs/architecture" / entry["file"]).read_text(encoding="utf-8")
        for entry in catalog["flows"]
    ]
    sections = re.split(r"(?m)^### \d+\. ", block)[1:]
    for section, entry in zip(sections, catalog["flows"], strict=True):
        assert entry["description"] in section
        assert f"(docs/architecture/{entry['file']})" in section
        assert f"(docs/architecture/{Path(entry['file']).with_suffix('.svg').as_posix()})" in section
        for source in entry["sources"]:
            assert f"({source['path']}#L{source['line']})" in section
            assert f"`{source['symbol']}`" in section
        for limitation in entry["limitations"]:
            assert f"- {limitation}" in section


def test_sincroniza_fontes_completas_na_ordem_do_catalogo(sample_root):
    result = run_sync(sample_root)
    assert result.returncode == 0, result.stdout + result.stderr
    text = (sample_root / "README.md").read_text(encoding="utf-8")
    assert re.findall(r"^### \d+\. (.+)$", text, re.MULTILINE) == ["Entrada íntegra", "Saída íntegra"]
    assert re.findall(r"```mermaid\n(.*?)```", text, re.DOTALL) == [
        'flowchart TB\n  A["Entrada"] --> B{"Aceitar?"}\n  B -->|"não"| C["Recusar"]\n',
        'flowchart LR\n  X["Dado"] -. "composição" .-> Y["Saída"]\n',
    ]


def test_preserva_bytes_fora_do_bloco_e_posicao_de_mira(sample_root):
    readme = sample_root / "README.md"
    before = readme.read_bytes()
    result = run_sync(sample_root)
    assert result.returncode == 0, result.stdout + result.stderr
    after = readme.read_bytes()
    start, end = after.index(START.encode()), after.index(END.encode()) + len(END)
    assert after[:start] + after[end + 2:] == before
    assert end < after.index(ANCHOR.encode())


def test_idempotencia_e_check_nao_escreve(sample_root):
    assert run_sync(sample_root).returncode == 0
    first = (sample_root / "README.md").read_bytes()
    assert run_sync(sample_root).returncode == 0
    assert (sample_root / "README.md").read_bytes() == first
    assert run_sync(sample_root, "--check").returncode == 0
    assert (sample_root / "README.md").read_bytes() == first


def test_check_recusa_fluxo_truncado_sem_modificar_documento(sample_root):
    assert run_sync(sample_root).returncode == 0
    readme = sample_root / "README.md"
    truncated = readme.read_bytes().replace(b'  B -->|"n', b'  Z -->|"n', 1)
    readme.write_bytes(truncated)
    result = run_sync(sample_root, "--check")
    assert result.returncode == 1, result.stdout + result.stderr
    assert readme.read_bytes() == truncated


def test_check_detecta_mudanca_na_fonte_e_regeneracao_restabelece_igualdade(sample_root):
    assert run_sync(sample_root).returncode == 0
    source = sample_root / "docs/architecture/flows/02-sample.mmd"
    source.write_text('flowchart LR\n  X["Dado"] --> Y["Nova aresta completa"]\n', encoding="utf-8")
    assert run_sync(sample_root, "--check").returncode == 1
    assert run_sync(sample_root).returncode == 0
    diagrams = re.findall(r"```mermaid\n(.*?)```", (sample_root / "README.md").read_text(encoding="utf-8"), re.DOTALL)
    assert diagrams[1] == 'flowchart LR\n  X["Dado"] --> Y["Nova aresta completa"]\n'


@pytest.mark.parametrize("bad_path", ["../../secret.mmd", "/tmp/secret.mmd", "flows\\secret.mmd"])
def test_caminho_de_fluxo_deve_permanecer_no_repositorio(sample_root, bad_path):
    readme = sample_root / "README.md"
    before = readme.read_bytes()
    catalog_path = sample_root / "docs/architecture/flows.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog["flows"][0]["file"] = bad_path
    catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
    result = run_sync(sample_root)
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stderr.startswith("Erro de sincronização:")
    assert readme.read_bytes() == before


def test_recusa_symlink_que_exponha_fonte_fora_do_repositorio(sample_root):
    readme = sample_root / "README.md"
    before = readme.read_bytes()
    outside = sample_root.parent / "outside.py"
    outside.write_text("private source", encoding="utf-8")
    source = sample_root / "src/core.py"
    source.unlink()
    source.symlink_to(outside)
    result = run_sync(sample_root)
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stderr.startswith("Erro de sincronização:")
    assert readme.read_bytes() == before


@pytest.mark.parametrize("markers", [START + START + END, END + START])
def test_marcadores_duplicados_ou_invertidos_recusados_sem_escrita(sample_root, markers):
    readme = sample_root / "README.md"
    before = (markers + "\n" + ANCHOR).encode()
    readme.write_bytes(before)
    result = run_sync(sample_root)
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stderr.startswith("Erro de sincronização:")
    assert readme.read_bytes() == before


def test_readme_alternativo_local_e_proibicao_de_escrita_fora_da_raiz(sample_root):
    alternate = sample_root / "GUIDE.md"
    alternate.write_text("# Guia\n\n" + ANCHOR + "\n", encoding="utf-8")
    main_before = (sample_root / "README.md").read_bytes()
    result = run_sync(sample_root, "--readme", "GUIDE.md")
    assert result.returncode == 0, result.stdout + result.stderr
    assert alternate.read_text(encoding="utf-8").count("```mermaid") == 2
    assert (sample_root / "README.md").read_bytes() == main_before
    outside = sample_root.parent / "private.md"
    outside.write_text("unchanged", encoding="utf-8")
    result = run_sync(sample_root, "--readme", str(outside))
    assert result.returncode == 2, result.stdout + result.stderr
    assert result.stderr.startswith("Erro de sincronização:")
    assert outside.read_text(encoding="utf-8") == "unchanged"
