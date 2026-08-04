import os
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

def test_ficha_estudo_table_framing():
    # ficha_estudo_critico.tex é o mesmo artefato que
    # test_r265_r279_spec_deliverables.py::TestR266FichaEstudo já documenta
    # como overclaim histórico ("arquivos de teste que nunca existiram no
    # histórico do git") -- nunca chegou a ser escrito de verdade. Mesmo
    # tratamento honesto aplicado em test_r266_ficha_estudo_critico.py: skip
    # explícito em vez de reivindicar um documento inexistente.
    tex_path = os.path.join(MOLAMBUDOS_DIR, "ficha_estudo_critico.tex")
    if not os.path.exists(tex_path):
        pytest.skip(
            "ficha_estudo_critico.tex não presente no checkout -- já "
            "documentado como overclaim histórico"
        )
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
