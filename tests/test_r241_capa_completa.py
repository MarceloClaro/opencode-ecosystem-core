import os
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

def test_capa_completa_file_exists():
    capa_tex_path = os.path.join(MOLAMBUDOS_DIR, "capa_completa.tex")
    assert os.path.exists(capa_tex_path), f"Arquivo não encontrado: {capa_tex_path}"
    with open(capa_tex_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "14.728in" in content, "Falta dimensão da largura total 14.728in"
    assert "10.417in" in content, "Falta dimensão da altura total 10.417in"
    assert "1.154in" in content, "Falta dimensão da lombada 1.154in"
    assert "6.197in" in content, "Falta dimensão da capa frontal 6.197in"

def test_capa_completa_pdf_compilation():
    pdf_path = os.path.join(MOLAMBUDOS_DIR, "capa_completa.pdf")
    assert os.path.exists(pdf_path), f"PDF da capa não encontrado: {pdf_path}"
    assert os.path.getsize(pdf_path) > 100000, "PDF da capa gerado está excessivamente pequeno ou corrompido"
