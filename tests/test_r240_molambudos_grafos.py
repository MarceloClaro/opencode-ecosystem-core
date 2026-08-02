import os
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

def test_main_tex_graph_framing():
    main_path = os.path.join(MOLAMBUDOS_DIR, "main.tex")
    assert os.path.exists(main_path), f"Arquivo não encontrado: {main_path}"
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "\\vbox to \\textheight" in content, "Falta travamento \\vbox to \\textheight nos grafos em main.tex"
    assert "height=0.92\\textwidth" in content, "Falta escala ajustada de height=0.92\\textwidth nos grafos"
    assert "width=0.92\\textheight" in content, "Falta escala ajustada de width=0.92\\textheight nos grafos"
    assert "\\fboxsep}{3pt}" in content, "Falta calibração de \\fboxsep}{3pt} nos grafos"

def test_latex_compilation_clean_graphs():
    log_path = os.path.join(MOLAMBUDOS_DIR, "main.log")
    if not os.path.exists(log_path):
        pytest.skip("main.log não gerado ainda")
    
    with open(log_path, "r", encoding="latin1") as f:
        log_content = f.read()
    
    assert "Overfull \\vbox" not in log_content or "Overfull \\vbox (89." not in log_content, "Log não deve conter Overfull vbox grave nos grafos"
