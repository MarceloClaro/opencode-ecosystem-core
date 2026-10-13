"""SPEC-978 — Pasta de auditoria + fichamento ABNT obrigatório (RED)."""
import json
from pathlib import Path


def test_r978_modulo_existe():
    import importlib.util
    assert importlib.util.find_spec("research.auditoria_fichamento") is not None, \
        "research/auditoria_fichamento.py ausente (RED)"


def test_r978_pasta_recorte_auditoria(tmp_path):
    try:
        from research.auditoria_fichamento import criar_pasta_auditoria, auditar_pasta, adicionar_recorte
    except ImportError:
        assert False, "API R-978 ausente (RED)"
        return
    base = tmp_path / "auditoria_fichamentos"
    meta = {"doi": "10.1371/journal.pone.0024352", "titulo": "Artigo Exemplo",
            "autores": ["Silva, João"], "ano": 2011, "fonte": "openalex",
            "licenca": "cc-by", "pdf_url": "https://exemplo.org/oa.pdf"}
    pasta = criar_pasta_auditoria(str(base), meta, pdf_bytes=b"%PDF-1.4 fake",
                                  runner_allowed=lambda m: {"allowed": True})
    assert Path(pasta).is_dir()
    assert (Path(pasta) / "metadados.json").exists()
    assert (Path(pasta) / "fichamento.md").exists()
    # fichamento inicial sem recortes reprova por cobertura (R-978.5)
    r0 = auditar_pasta(pasta, citacoes_manuscrito=["(SILVA, 2011, p. 3)"])
    assert r0["aprovado"] is False

    rec = {"trecho_literal": "trecho relevante com menos de quatrocentos caracteres",
           "pagina": "3", "autor": "SILVA", "ano": 2011,
           "justificativa_relevancia": "Sustenta o argumento central sobre o tema com evidência direta.",
           "id_trecho_manuscrito": "(SILVA, 2011, p. 3)"}
    adicionar_recorte(pasta, rec)
    r1 = auditar_pasta(pasta, citacoes_manuscrito=["(SILVA, 2011, p. 3)"])
    assert r1["aprovado"] is True
    fich = (Path(pasta) / "fichamento.md").read_text(encoding="utf-8")
    assert "SILVA" in fich and "2011" in fich and "p. 3" in fich


def test_r978_bloqueios_obrigatorios(tmp_path):
    try:
        from research.auditoria_fichamento import criar_pasta_auditoria, adicionar_recorte
    except ImportError:
        assert False, "API R-978 ausente (RED)"
        return
    base = tmp_path / "a"
    meta = {"doi": "10.1038/nature12373", "titulo": "Fechado", "autores": ["A"], "ano": 2013}
    # fechado não baixa PDF
    p = criar_pasta_auditoria(str(base), meta, pdf_bytes=b"%PDF-1.4 x",
                              runner_allowed=lambda m: {"allowed": False, "reason": "closed_access"})
    assert not (Path(p) / "artigo.pdf").exists()
    assert (Path(p) / "sem_pdf.json").exists()
    # recorte longo ou sem justificativa deve falhar
    for bad in [
        {"trecho_literal": "x" * 401, "pagina": "1", "autor": "A", "ano": 2013,
         "justificativa_relevancia": "Justificativa suficiente com mais de vinte caracteres.",
         "id_trecho_manuscrito": "m1"},
        {"trecho_literal": "curto", "pagina": "", "autor": "A", "ano": 2013,
         "justificativa_relevancia": "Justificativa suficiente com mais de vinte caracteres.",
         "id_trecho_manuscrito": "m1"},
        {"trecho_literal": "curto", "pagina": "1", "autor": "A", "ano": 2013,
         "justificativa_relevancia": "curta",
         "id_trecho_manuscrito": "m1"},
    ]:
        try:
            adicionar_recorte(p, bad)
            assert False, f"recorte inválido deveria falhar: {bad['trecho_literal'][:20]}"
        except ValueError:
            pass
