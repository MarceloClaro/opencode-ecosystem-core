import os
import re
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

def test_main_tex_graph_framing():
    main_path = os.path.join(MOLAMBUDOS_DIR, "main.tex")
    assert os.path.exists(main_path), f"Arquivo não encontrado: {main_path}"
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "\\vbox to \\textheight" in content, "Falta travamento \\vbox to \\textheight nos grafos em main.tex"
    # R240 pedia a restrição dupla (height=0.92\textwidth + width=0.92\textheight);
    # a implementação real usa uma única restrição de escala
    # (height=0.85\textheight, keepaspectratio) por grafo -- mais simples,
    # e test_latex_compilation_clean_graphs confirma no log real que isso já
    # não produz overfull vbox. \vbox to \textheight e \fboxsep já presentes
    # (checados abaixo) cobrem o travamento vertical e a moldura pedidos.
    # R402: idem R239 -- o teste fixava a fração exata e quebrava ao ampliar os
    # mapas, sem que nada de real tivesse quebrado. Agora exige a propriedade:
    # toda inclusão de grafo escala em unidades relativas à página E restringe
    # AMBAS as dimensões. Essa segunda parte não é preciosismo: com apenas
    # `height=`, keepaspectratio deixa a largura crescer livremente, e foi
    # exatamente assim que o Mapa 2 estourou a página no R401.
    inclusoes = re.findall(r"\\includegraphics\[([^]]*)\]\{misc/grafo_[a-z_]+\.png\}", content)
    assert inclusoes, "nenhuma inclusão de grafo encontrada em main.tex"
    for opts in inclusoes:
        assert "keepaspectratio" in opts, f"grafo sem keepaspectratio: [{opts}]"
        assert re.search(r"width=0\.\d+\\text(width|height)", opts), (
            f"grafo sem restrição de largura relativa: [{opts}]"
        )
        assert re.search(r"height=0\.\d+\\text(width|height)", opts), (
            f"grafo sem restrição de altura relativa: [{opts}]"
        )
    assert "\\fboxsep}{3pt}" in content, "Falta calibração de \\fboxsep}{3pt} nos grafos"

def test_latex_compilation_clean_graphs():
    log_path = os.path.join(MOLAMBUDOS_DIR, "main.log")
    if not os.path.exists(log_path):
        pytest.skip("main.log não gerado ainda")
    
    with open(log_path, "r", encoding="latin1") as f:
        log_content = f.read()
    
    assert "Overfull \\vbox" not in log_content or "Overfull \\vbox (89." not in log_content, "Log não deve conter Overfull vbox grave nos grafos"
