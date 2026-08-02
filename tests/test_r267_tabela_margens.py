import os
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

def test_ficha_estudo_table_framing():
    tex_path = os.path.join(MOLAMBUDOS_DIR, "ficha_estudo_critico.tex")
    assert os.path.exists(tex_path), f"Arquivo não encontrado: {tex_path}"
    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "\\resizebox{\\linewidth}" in content or "\\begin{tabular}{p{" in content, "Falta enquadramento da tabela nas margens da página"

def test_no_table_overfull_in_log():
    log_path = os.path.join(MOLAMBUDOS_DIR, "ficha_estudo_critico.log")
    if not os.path.exists(log_path):
        pytest.skip("Log não gerado ainda")
    
    with open(log_path, "r", encoding="latin1") as f:
        log_content = f.read()
    
    assert "Overfull \\hbox (134." not in log_content, "Estouro de margem de 134pt na tabela ainda presente no log"
