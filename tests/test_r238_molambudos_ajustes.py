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

def test_cont_01_chancela_paratextual():
    cont01_path = os.path.join(MOLAMBUDOS_DIR, "fragmentos/cont/CONT-01.tex")
    assert os.path.exists(cont01_path), f"Arquivo não encontrado: {cont01_path}"
    with open(cont01_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "Arquivista" in content, "Falta nota/chancela do Arquivista em CONT-01"
    assert "CONT-02" in content or "destruídos" in content or "subtraídos" in content, "Falta explicação paratextual sobre fragmentos ausentes em CONT-01"

def test_main_tex_illusionismo_pagina_62():
    main_path = os.path.join(MOLAMBUDOS_DIR, "main.tex")
    assert os.path.exists(main_path), f"Arquivo não encontrado: {main_path}"
    with open(main_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "Sessenta e dois" in content or "62" in content, "Falta referência ao número 62 e illusionismo no epílogo em main.tex"
