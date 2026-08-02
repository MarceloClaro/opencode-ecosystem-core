import os
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

def test_ficha_estudo_critico_tex_exists():
    tex_path = os.path.join(MOLAMBUDOS_DIR, "ficha_estudo_critico.tex")
    assert os.path.exists(tex_path), f"Arquivo não encontrado: {tex_path}"
    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "NoologicalScanner" in content or "noológica" in content, "Falta menção às métricas noológicas"
    assert "ScientificReasoningScanner" in content or "falseabilidade" in content, "Falta menção ao scanner científico"
    assert "PotentialityScanner" in content or "potencialidades" in content, "Falta menção ao scanner de potencialidade"
    assert "Barbacena" in content, "Falta menção histórica a Barbacena"

def test_ficha_estudo_critico_pdf_compilation():
    pdf_path = os.path.join(MOLAMBUDOS_DIR, "ficha_estudo_critico.pdf")
    assert os.path.exists(pdf_path), f"PDF da ficha não encontrado: {pdf_path}"
    assert os.path.getsize(pdf_path) > 50000, "PDF da ficha de estudo crítico está excessivamente pequeno"
