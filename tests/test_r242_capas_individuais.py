import os
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

@pytest.mark.parametrize("file_prefix", ["capa_frontal", "contracapa", "lombada"])
def test_capas_individuais_files_exist(file_prefix):
    tex_path = os.path.join(MOLAMBUDOS_DIR, f"{file_prefix}.tex")
    assert os.path.exists(tex_path), f"Arquivo .tex não encontrado: {tex_path}"

@pytest.mark.parametrize("file_prefix", ["capa_frontal", "contracapa", "lombada"])
def test_capas_individuais_pdfs_exist(file_prefix):
    pdf_path = os.path.join(MOLAMBUDOS_DIR, f"{file_prefix}.pdf")
    assert os.path.exists(pdf_path), f"Arquivo .pdf não encontrado: {pdf_path}"
    assert os.path.getsize(pdf_path) > 10000, f"PDF {file_prefix}.pdf muito pequeno ou corrompido"
