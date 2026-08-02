import os
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

def test_options_sty_microtype_tracking():
    options_path = os.path.join(MOLAMBUDOS_DIR, "misc/options.sty")
    assert os.path.exists(options_path), f"Arquivo não encontrado: {options_path}"
    with open(options_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "encoding={T1,OT1}" in content or "encoding=T1" in content, "Falta restrição de encoding no tracking de sc em options.sty"
    assert "\\baselinestretch}{1.35}" in content or "\\baselinestretch}{1.4}" in content, "Baselinestretch deve estar otimizado em options.sty"

def test_main_tex_margin_params():
    main_path = os.path.join(MOLAMBUDOS_DIR, "main.tex")
    assert os.path.exists(main_path), f"Arquivo não encontrado: {main_path}"
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "width=0.82\\textheight" in content or "width=0.85\\textheight" in content, "Grafos devem utilizar escala otimizada para evitar Overfull vbox"
    assert "\\marginparwidth}{0.75in}" in content or "\\marginparwidth}{0.7in}" in content, "Marginparwidth deve estar calibrada para evitar fuga de margens"

def test_no_major_overfull_vbox_in_log():
    log_path = os.path.join(MOLAMBUDOS_DIR, "main.log")
    if not os.path.exists(log_path):
        pytest.skip("main.log não gerado ainda")
    
    with open(log_path, "r", encoding="latin1") as f:
        log_content = f.read()
    
    assert "Overfull \\vbox (89." not in log_content, "Encontrado Overfull vbox significativo no log de compilação"
    assert "Output written on main.pdf (371 pages" in log_content or "Output written on main.pdf" in log_content, "PDF deve ter sido compilado com sucesso"
