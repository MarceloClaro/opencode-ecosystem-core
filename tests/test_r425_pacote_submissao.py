"""Testes do pacote final de submissão RBEP (R425).

SPEC-935-R425: verifica a existência do ZIP, a estrutura de pastas, a
presença dos artefatos obrigatórios, a ausência de temporários e a
integridade SHA-256 via MANIFEST_SUBMISSAO.json.
"""
import hashlib
import json
import os
import zipfile
from datetime import date
from pathlib import Path

import pytest

PAPER = Path(__file__).resolve().parent.parent / "academic" / "papers" / "arm_education_audit"
SUBMISSION_OUTPUT = PAPER / "outputs" / "submission"
ZIP_ENV_VAR = "RBEP_SUBMISSION_ZIP"

REQUERIDOS = [
    "01_manuscrito/ARTIGO_RBEP_SUBMISSAO.docx",
    "01_manuscrito/ARTIGO_RBEP_SUBMISSAO.pdf",
    "01_manuscrito/ARTIGO_RBEP_SUBMISSAO.md",
    "02_carta/CARTA_AO_EDITOR.md",
    "03_revisao/peer_review_r422.md",
    "README_SUBMISSAO.md",
    "MANIFEST_SUBMISSAO.json",
]


def select_submission_zip(
    output_dir: Path,
    *,
    zip_path: Path | None = None,
    submission_date: date | None = None,
) -> Path | None:
    """Seleciona um artefato injetado ou a opção disponível de modo estável."""

    if zip_path is not None:
        return zip_path
    if submission_date is not None:
        return output_dir / (
            "ARTIGO_RBEP_SUBMISSAO_submissao_"
            f"{submission_date.isoformat()}.zip"
        )
    candidates = sorted(output_dir.glob("ARTIGO_RBEP_SUBMISSAO_submissao_*.zip"))
    return candidates[-1] if candidates else None


def test_selecao_zip_injetavel_e_deterministica(tmp_path: Path):
    """O teste não depende da data corrente nem de um ZIP versionado no checkout."""

    older = tmp_path / "ARTIGO_RBEP_SUBMISSAO_submissao_2026-01-01.zip"
    newer = tmp_path / "ARTIGO_RBEP_SUBMISSAO_submissao_2026-02-01.zip"
    injected = tmp_path / "artefato-injetado.zip"
    older.touch()
    newer.touch()

    assert select_submission_zip(tmp_path) == newer
    assert select_submission_zip(
        tmp_path,
        submission_date=date(2026, 1, 1),
    ) == older
    assert select_submission_zip(tmp_path, zip_path=injected) == injected


@pytest.fixture(scope="module")
def submission_zip() -> Path:
    """Entrega o ZIP opcional configurado ou pula explicitamente a validação."""

    configured_path = os.environ.get(ZIP_ENV_VAR)
    injected_path = Path(configured_path).expanduser() if configured_path else None
    selected = select_submission_zip(SUBMISSION_OUTPUT, zip_path=injected_path)
    if selected is None or not selected.is_file():
        pytest.skip(
            "artefato opcional de submissão ausente; "
            f"defina {ZIP_ENV_VAR} para validar um ZIP específico"
        )
    return selected


@pytest.fixture(scope="module")
def zf(submission_zip: Path):
    with zipfile.ZipFile(submission_zip) as f:
        yield f


def test_pacote_existe(submission_zip: Path):
    assert submission_zip.is_file(), "pacote ZIP de submissão ausente"


def test_estrutura_obrigatoria(zf):
    nomes = set(zf.namelist())
    for req in REQUERIDOS:
        assert req in nomes, f"arquivo obrigatório ausente no pacote: {req}"


def test_pastas_organizadas(zf):
    nomes = set(zf.namelist())
    for pasta in ["01_manuscrito/", "02_carta/", "03_revisao/", "04_dados/"]:
        assert any(n.startswith(pasta) for n in nomes), f"pasta ausente: {pasta}"


def test_sem_temporarios(zf):
    for nome in zf.namelist():
        sufixo = Path(nome).suffix
        assert sufixo not in {".aux", ".log", ".out"}, f"temporário no pacote: {nome}"
        assert "__pycache__" not in nome


def test_manifest_sha256(zf):
    manifest = json.loads(zf.read("MANIFEST_SUBMISSAO.json").decode("utf-8"))
    assert manifest["autor"] == "Marcelo Claro Laranjeira"
    assert "orcid.org/0000-0001-8996-2887" in manifest["orcid"]
    assert len(manifest["arquivos"]) >= 5
    verificados = 0
    for entrada in manifest["arquivos"]:
        if verificados >= 5:
            break
        conteudo = zf.read(entrada["arquivo"])
        assert hashlib.sha256(conteudo).hexdigest() == entrada["sha256"], \
            f"hash divergente: {entrada['arquivo']}"
        verificados += 1
    assert verificados >= 5, "manifest precisa ter ao menos 5 entradas verificáveis"


def test_readme_sem_overclaim(zf):
    readme = zf.read("README_SUBMISSAO.md").decode("utf-8")
    assert "candidato a submissão" in readme
    for bloqueado in ["aprovado", "validado", "Qualis A1"]:
        assert bloqueado not in readme, f"overclaim no README: {bloqueado}"


def test_dados_proveniencia_presentes(zf):
    nomes = zf.namelist()
    prov = [n for n in nomes if n.startswith("04_dados/provenance") and n.endswith(".json")]
    assert len(prov) >= 3, "esperava ao menos 3 JSONs de proveniência em 04_dados/"


def test_docx_com_autoria(zf):
    import io
    from docx import Document
    docx_bytes = zf.read("01_manuscrito/ARTIGO_RBEP_SUBMISSAO.docx")
    doc = Document(io.BytesIO(docx_bytes))
    texto = "\n".join(p.text for p in doc.paragraphs)
    assert "Marcelo Claro Laranjeira" in texto
    assert "orcid.org/0000-0001-8996-2887" in texto
