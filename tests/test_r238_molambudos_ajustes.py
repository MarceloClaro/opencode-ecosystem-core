import os
import pytest

MOLAMBUDOS_DIR = "/home/marceloclaro/opencode-ecosystem-core/projetos/molambudos/Molambudos_VictoriaRegia"

def test_doc_08_psiquiatria_pelagra_cid11():
    doc08_path = os.path.join(MOLAMBUDOS_DIR, "fragmentos/doc/DOC-08.tex")
    assert os.path.exists(doc08_path), f"Arquivo não encontrado: {doc08_path}"
    with open(doc08_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "Pelagra" in content or "pelagra" in content, "Falta diagnóstico de Pelagra em DOC-08"
    assert "6D50" in content, "Falta CID-11 6D50 em DOC-08"
    assert "avitaminose" in content or "desnutrição" in content, "Falta menção à etiologia de avitaminose/desnutrição em DOC-08"

def test_cont_fragments_gap_no_longer_needs_paratextual_excuse():
    # R238/R3 pedia uma nota do Arquivista em CONT-01 explicando que
    # CONT-02/03/05/06/08/09/11/12 tinham sido "destruídos ou subtraídos" --
    # verdade quando a spec foi escrita, mas os ciclos R376/R377 escreveram
    # esses fragmentos de verdade (220-1189 palavras cada). Adicionar a nota
    # de "destruído" agora contradiria o próprio conteúdo do livro -- a
    # invariante real e atual é a inversa: esses fragmentos devem *existir*.
    for numero in ("02", "03", "05", "06", "08", "09", "11", "12"):
        path = os.path.join(MOLAMBUDOS_DIR, f"fragmentos/cont/CONT-{numero}.tex")
        assert os.path.exists(path), f"CONT-{numero}.tex deveria existir (R376/R377)"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert len(content.split()) > 50, f"CONT-{numero}.tex existe mas está vazio/raso"

def test_main_tex_illusionismo_pagina_62():
    main_path = os.path.join(MOLAMBUDOS_DIR, "main.tex")
    assert os.path.exists(main_path), f"Arquivo não encontrado: {main_path}"
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "Sessenta e dois" in content or "62" in content, "Falta referência ao número 62 e illusionismo no epílogo em main.tex"
