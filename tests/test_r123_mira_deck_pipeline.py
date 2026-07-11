# -*- coding: utf-8 -*-
"""
Testes R123 — Pipeline MIRA de Apresentações Científicas
=================================================================
Escritos ANTES da implementação (TDD). Portam para teste as regras do
método MIRA (livro "MIRA" + sandeco/mira-animator, cap. 2-3):

  - Regra Zero: todo card entra com coreografia e segue em loop
    perpétuo (CSS infinite); slide parado é defeito
  - Título ≤ 6 palavras
  - Linha de montagem de 6 estágios com fronteiras limpas:
    extract → plan → copywrite → build → animate → validate
  - Cards de vidro (glassmorphism) com navegação card-a-card
  - Formato do card acompanha o formato da ideia (quote/code/grid/
    concept)
  - Inspetor final emite relatório de conformidade

Requisitos: SPEC-935-R123.
"""

import os

import pytest

MANUSCRITO = """# Inteligência Artificial em Odontologia

## O pipeline de diagnóstico por imagem

O fluxo segue etapas encadeadas: aquisição, pré-processamento,
segmentação e classificação. Cada etapa transforma a saída da
anterior, como um workflow de estações.

## O que dizem os especialistas sobre confiança

A confiança clínica precisa ser conquistada gradualmente.

> "Nenhum modelo substitui o julgamento clínico; ele o amplifica."

Essa citação resume o consenso da literatura recente.

## Exemplo de código de inferência

O trecho abaixo demonstra a chamada mínima de inferência:

```python
resultado = modelo.predict(imagem_radiografica)
print(resultado.classe, resultado.confianca)
```

## Aplicações paralelas na clínica

- Detecção de cáries em radiografias interproximais
- Segmentação de canais radiculares em CBCT
- Triagem de lesões de mucosa em fotografias
- Previsão de sucesso em implantes
"""


@pytest.fixture
def pipeline():
    from illustrations.mira_deck import MiraDeckPipeline
    return MiraDeckPipeline()


@pytest.fixture
def briefing(pipeline):
    return pipeline.extract(MANUSCRITO)


@pytest.fixture
def deck_validado(pipeline, tmp_path):
    """Deck completo gerado pela linha inteira num diretório temporário."""
    report = pipeline.run(MANUSCRITO, str(tmp_path))
    deck_html = (tmp_path / "deck.html").read_text(encoding="utf-8")
    return report, deck_html, tmp_path


# ----------------------------------------------------------------------
# Estágio 1 — extract
# ----------------------------------------------------------------------
class TestExtract:
    def test_captura_titulo_do_documento(self, briefing):
        assert briefing.title == "Inteligência Artificial em Odontologia"

    def test_uma_secao_por_h2(self, briefing):
        assert len(briefing.sections) == 4
        titulos = [s.title for s in briefing.sections]
        assert "O pipeline de diagnóstico por imagem" in titulos

    def test_detecta_citacao(self, briefing):
        sec = next(s for s in briefing.sections if "especialistas" in s.title)
        assert sec.quote is not None
        assert "julgamento clínico" in sec.quote

    def test_detecta_bloco_de_codigo(self, briefing):
        sec = next(s for s in briefing.sections if "código" in s.title)
        assert sec.code is not None
        assert "modelo.predict" in sec.code

    def test_detecta_itens_paralelos(self, briefing):
        sec = next(s for s in briefing.sections if "Aplicações" in s.title)
        assert len(sec.key_points) >= 3

    def test_secao_sem_marcadores_nao_tem_citacao_nem_codigo(self, briefing):
        sec = next(s for s in briefing.sections if "pipeline" in s.title)
        assert sec.quote is None
        assert sec.code is None


# ----------------------------------------------------------------------
# Estágio 2 — plan
# ----------------------------------------------------------------------
class TestPlan:
    def test_capa_e_encerramento(self, pipeline, briefing):
        plan = pipeline.plan(briefing)
        kinds = [s.kind for s in plan.slides]
        assert kinds[0] == "cover"
        assert kinds[-1] == "closing"

    def test_um_slide_por_secao(self, pipeline, briefing):
        plan = pipeline.plan(briefing)
        # capa + 4 seções + encerramento
        assert len(plan.slides) == 6

    def test_tipo_de_card_segue_formato_da_ideia(self, pipeline, briefing):
        plan = pipeline.plan(briefing)
        by_title = {s.title: s.kind for s in plan.slides}
        # citação → quote
        assert by_title[next(k for k in by_title if "especialistas" in k)] == "quote"
        # código → code
        assert by_title[next(k for k in by_title if "código" in k)] == "code"
        # lista de itens paralelos → grid
        assert by_title[next(k for k in by_title if "Aplicações" in k)] == "grid"
        # padrão → concept (metáfora animada)
        assert by_title[next(k for k in by_title if "pipeline" in k)] == "concept"

    def test_concept_recebe_metafora_do_catalogo(self, pipeline, briefing):
        plan = pipeline.plan(briefing)
        concept = next(s for s in plan.slides if s.kind == "concept")
        assert concept.metaphor_key is not None


# ----------------------------------------------------------------------
# Estágio 3 — copywrite
# ----------------------------------------------------------------------
class TestCopywrite:
    def test_nenhum_titulo_passa_de_seis_palavras(self, pipeline, briefing):
        plan = pipeline.copywrite(pipeline.plan(briefing))
        for s in plan.slides:
            assert len(s.title.split()) <= 6, s.title

    def test_preserva_numero_de_slides(self, pipeline, briefing):
        plan = pipeline.plan(briefing)
        refinado = pipeline.copywrite(plan)
        assert len(refinado.slides) == len(plan.slides)


# ----------------------------------------------------------------------
# Estágio 4 — build
# ----------------------------------------------------------------------
class TestBuild:
    def test_html_unico_autocontido(self, pipeline, briefing):
        deck = pipeline.build(pipeline.copywrite(pipeline.plan(briefing)))
        assert deck.html.lstrip().startswith("<!DOCTYPE html>")
        # nada de recursos externos (o xmlns do SVG não conta)
        assert 'src="http' not in deck.html
        assert 'href="http' not in deck.html
        assert "<link" not in deck.html

    def test_cards_de_vidro(self, pipeline, briefing):
        deck = pipeline.build(pipeline.copywrite(pipeline.plan(briefing)))
        assert "backdrop-filter" in deck.html

    def test_navegacao_card_a_card(self, pipeline, briefing):
        deck = pipeline.build(pipeline.copywrite(pipeline.plan(briefing)))
        assert "keydown" in deck.html           # setas do teclado
        assert "onclick" in deck.html.lower()   # botões prev/next


# ----------------------------------------------------------------------
# Estágio 5 — animate (Regra Zero)
# ----------------------------------------------------------------------
class TestAnimate:
    def test_build_ainda_nao_tem_loop(self, pipeline, briefing):
        deck = pipeline.build(pipeline.copywrite(pipeline.plan(briefing)))
        assert "infinite" not in deck.html

    def test_animate_garante_regra_zero(self, pipeline, briefing):
        deck = pipeline.build(pipeline.copywrite(pipeline.plan(briefing)))
        deck = pipeline.animate(deck)
        assert "@keyframes" in deck.html
        assert "infinite" in deck.html          # loop perpétuo

    def test_concept_embute_svg_da_metafora(self, pipeline, briefing):
        deck = pipeline.animate(pipeline.build(pipeline.copywrite(pipeline.plan(briefing))))
        assert 'class="anim-stage"' in deck.html


# ----------------------------------------------------------------------
# Estágio 6 — validate (inspetor de conformidade)
# ----------------------------------------------------------------------
class TestValidate:
    def test_deck_da_propria_linha_passa(self, pipeline, briefing):
        deck = pipeline.animate(pipeline.build(pipeline.copywrite(pipeline.plan(briefing))))
        report = pipeline.validate(deck)
        assert report.passed is True
        assert report.violations == []

    def test_detecta_ausencia_de_loop(self, pipeline, briefing):
        deck = pipeline.animate(pipeline.build(pipeline.copywrite(pipeline.plan(briefing))))
        deck.html = deck.html.replace("infinite", "once")  # adultera a Regra Zero
        report = pipeline.validate(deck)
        assert report.passed is False
        assert any("loop" in v.lower() or "infinite" in v.lower() for v in report.violations)

    def test_detecta_titulo_longo(self, pipeline, briefing):
        deck = pipeline.animate(pipeline.build(pipeline.copywrite(pipeline.plan(briefing))))
        deck.slides[1].title = "Um título deliberadamente longo com sete palavras"
        report = pipeline.validate(deck)
        assert report.passed is False
        assert any("palavra" in v.lower() or "título" in v.lower() for v in report.violations)


# ----------------------------------------------------------------------
# Linha completa — run
# ----------------------------------------------------------------------
class TestRun:
    def test_grava_deck_e_conformidade(self, deck_validado):
        report, deck_html, out = deck_validado
        assert (out / "deck.html").exists()
        assert (out / "CONFORMIDADE.md").exists()
        assert report.passed is True

    def test_deck_gravado_respeita_regra_zero(self, deck_validado):
        _report, deck_html, _out = deck_validado
        assert "infinite" in deck_html
        assert "backdrop-filter" in deck_html

    def test_cada_estagio_e_chamavel_isoladamente(self, pipeline):
        # consertar a peça, não a fábrica: a esteira para nas juntas
        b = pipeline.extract(MANUSCRITO)
        p = pipeline.plan(b)
        c = pipeline.copywrite(p)
        d = pipeline.build(c)
        a = pipeline.animate(d)
        r = pipeline.validate(a)
        assert r.passed is True


# ----------------------------------------------------------------------
# Integração com o orquestrador — present()
# ----------------------------------------------------------------------
class TestOrchestratorPresent:
    def test_present_gera_deck_da_producao(self, tmp_path):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        prod = tmp_path / "producao"
        prod.mkdir()
        (prod / "manuscrito.md").write_text(MANUSCRITO, encoding="utf-8")

        orch = MarceloClaroOrchestrator()
        result = orch.present(str(prod))

        deck = prod / "apresentacao" / "deck.html"
        assert deck.exists()
        assert result["passed"] is True
        assert "deck" in result

    def test_present_sem_manuscrito_reporta_erro(self, tmp_path):
        from marceloclaro.orchestrator import MarceloClaroOrchestrator
        prod = tmp_path / "vazia"
        prod.mkdir()
        orch = MarceloClaroOrchestrator()
        result = orch.present(str(prod))
        assert result.get("ok") is False or result.get("error")
