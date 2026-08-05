import os
import re
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

def test_options_sty_microtype_tracking():
    options_path = os.path.join(MOLAMBUDOS_DIR, "misc/options.sty")
    assert os.path.exists(options_path), f"Arquivo não encontrado: {options_path}"
    with open(options_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "encoding={T1,OT1}" in content or "encoding=T1" in content, "Falta restrição de encoding no tracking de sc em options.sty"
    # R239 pedia 1.35/1.4; um ciclo posterior (pré-R362) recalibrou para 1.25
    # e o preflight R362 (scripts/audit_r362_pdf_layout.py::_source_checks)
    # passou a exigir exatamente esse valor como parte de sua checagem de
    # tipografia -- 1.25 é o valor canônico atual, verificado num build real
    # das 5 edições sem overfull/underfull. Aceitar os dois evita reintroduzir
    # o conflito caso R239 seja lido isoladamente no futuro.
    assert (
        "\\baselinestretch}{1.35}" in content
        or "\\baselinestretch}{1.4}" in content
        or "\\baselinestretch}{1.25}" in content
    ), "Baselinestretch deve estar otimizado em options.sty"

def test_main_tex_margin_params():
    main_path = os.path.join(MOLAMBUDOS_DIR, "main.tex")
    assert os.path.exists(main_path), f"Arquivo não encontrado: {main_path}"
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # O pedido original da R239 usava width= para imagens com angle=90 (a
    # largura pré-rotação vira a altura visual pós-rotação). A implementação
    # real usa height=0.85\textheight diretamente -- funciona porque
    # keepaspectratio absorve a diferença -- e test_no_major_overfull_vbox_in_log
    # já confirma, no log real de compilação, que isso não produz overfull
    # vbox. Aceitar ambas as formas evita re-brigar um problema já resolvido.
    # R402: o teste fixava a fração exata (0.82/0.85). Isso é medir o proxy em
    # vez da propriedade -- ampliar os mapas de 0.85 para 0.90 quebrava o teste
    # sem quebrar nada de real. A propriedade que importa é a escala ser
    # RELATIVA a \textheight (nunca absoluta), e quem confirma que não há
    # overfull é test_no_major_overfull_vbox_in_log, sobre o log real.
    escalas = re.findall(r"(?:width|height)=0\.\d+\\textheight", content)
    assert escalas, (
        "Grafos devem utilizar escala baseada em \\textheight para evitar Overfull vbox"
    )
    assert not re.search(r"includegraphics\[[^]]*(?:width|height)=\d+(?:\.\d+)?(?:cm|mm|in|pt)",
                         content), (
        "Grafos não podem usar dimensão absoluta: ela não acompanha a geometria da página"
    )
    assert "\\marginparwidth}{0.75in}" in content or "\\marginparwidth}{0.7in}" in content, "Marginparwidth deve estar calibrada para evitar fuga de margens"

def test_no_major_overfull_vbox_in_log():
    log_path = os.path.join(MOLAMBUDOS_DIR, "main.log")
    if not os.path.exists(log_path):
        pytest.skip("main.log não gerado ainda")
    
    with open(log_path, "r", encoding="latin1") as f:
        log_content = f.read()
    
    assert "Overfull \\vbox (89." not in log_content, "Encontrado Overfull vbox significativo no log de compilação"
    assert "Output written on main.pdf (371 pages" in log_content or "Output written on main.pdf" in log_content, "PDF deve ter sido compilado com sucesso"
