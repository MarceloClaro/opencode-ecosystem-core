"""Testes do pacote final de submissão RBEP (R425).

SPEC-935-R425: verifica a existência do ZIP, a estrutura de pastas, a
presença dos artefatos obrigatórios, a ausência de temporários e a
integridade SHA-256 via MANIFEST_SUBMISSAO.json.
"""
import hashlib
import json
import zipfile
from datetime import date
from pathlib import Path

import pytest

PAPER = Path(__file__).resolve().parent.parent / "academic" / "papers" / "arm_education_audit"
ZIP = PAPER / "outputs" / "submission" / f"ARTIGO_RBEP_SUBMISSAO_submissao_{date.today().isoformat()}.zip"

REQUERIDOS = [
    "01_manuscrito/ARTIGO_RBEP_SUBMISSAO.docx",
    "01_manuscrito/ARTIGO_RBEP_SUBMISSAO.pdf",
    "01_manuscrito/ARTIGO_RBEP_SUBMISSAO.md",
    "02_carta/CARTA_AO_EDITOR.md",
    "03_revisao/peer_review_r422.md",
    "README_SUBMISSAO.md",
    "MANIFEST_SUBMISSAO.json",
]


@pytest.fixture(scope="module")
def zf():
    if not ZIP.exists():
        pytest.skip(f"pacote não gerado: {ZIP}")
    with zipfile.ZipFile(ZIP) as f:
        yield f


def test_pacote_existe():
    assert ZIP.exists(), "pacote ZIP de submissão ausente"


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
