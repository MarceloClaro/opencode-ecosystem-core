# -*- coding: utf-8 -*-
"""
Testes R141 — Engine ocr-vision (SPEC-1001)
============================================
TDD do engine opcional de OCR para documentos antigos: OpenCV → remoção de
assinatura → PaddleOCR → correção contextual por Vision LLM. O foco dos
testes é o PRINCÍPIO INEGOCIÁVEL da spec — fidelidade > fluência: a correção
do LLM é sugestão que só é aplicada quando a divergência é baixa (typo de
OCR); reescritas divergentes NUNCA são aplicadas, apenas marcadas para
revisão. Toda a superfície é testada por injeção de dependência, sem exigir
opencv/paddleocr/modelo de visão.

Requisitos: SPEC-1001.
"""
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ── Fakes injetáveis (duck typing) ───────────────────────────────────

class _FakePreprocessor:
    def __init__(self):
        self.called = False
    def process(self, image):
        self.called = True
        return {"stage": "preprocessed", "src": image}


class _FakeSignatureRemover:
    def __init__(self):
        self.called = False
    def remove(self, image):
        self.called = True
        return {"stage": "no_signature", "src": image}


class _FakeOCR:
    """Devolve (texto, confiança) fixos — simula PaddleOCR."""
    def __init__(self, text="documento antigo", conf=0.7):
        self._text = text
        self._conf = conf
    def read(self, image):
        return self._text, self._conf


class _FakeCorrector:
    """Simula o Vision LLM: devolve a sugestão fornecida no construtor."""
    def __init__(self, suggestion):
        self._suggestion = suggestion
        self.last_context = None
    def suggest(self, ocr_text, context=""):
        self.last_context = context
        return self._suggestion


class _FakePageLoader:
    def __init__(self, n_pages=2):
        self._pages = [f"img{i}" for i in range(n_pages)]
    def load(self, pdf_path):
        return self._pages


def _engine(**kw):
    from pdf2latex.engines.ocr_vision import OcrVisionEngine
    return OcrVisionEngine(**kw)


# ── CA-1 / CA-2: registro e disponibilidade ──────────────────────────

def test_ca1_registrado_em_list_engines():
    from pdf2latex.engine_registry import list_engines
    engines = {e["name"]: e for e in list_engines()}
    assert "ocr-vision" in engines, "engine ocr-vision não registrado"
    assert engines["ocr-vision"]["requires_gpu"] is False


def test_ca2_is_available_bool_e_injecao():
    e_sem = _engine()
    assert isinstance(e_sem.is_available(), bool)  # não quebra sem deps
    e_com = _engine(ocr=_FakeOCR())
    assert e_com.is_available() is True  # componentes injetados → disponível


def test_metadata_menciona_fidelidade():
    e = _engine()
    assert e.name == "ocr-vision"
    desc = e.description.lower()
    assert "paddleocr" in desc or "ocr" in desc
    # A descrição deve deixar claro o princípio: não reescreve cego.
    assert "cego" in desc or "sugere" in desc or "confian" in desc


# ── CA-3: política de correção (núcleo da fidelidade) ─────────────────

def test_ca3_sugestao_vazia_mantem_ocr():
    from pdf2latex.engines.ocr_vision import apply_correction_policy
    out = apply_correction_policy("texto do ocr", "", ocr_confidence=0.5)
    assert out.replaced is False and out.flagged is False
    assert out.text == "texto do ocr"


def test_ca3_identico_mantem_ocr():
    from pdf2latex.engines.ocr_vision import apply_correction_policy
    out = apply_correction_policy("mesma coisa", "mesma coisa", ocr_confidence=0.5)
    assert out.replaced is False
    assert out.text == "mesma coisa"


def test_ca3_divergencia_baixa_aceita_sugestao():
    from pdf2latex.engines.ocr_vision import apply_correction_policy
    # typo de OCR: "0" no lugar de "o", "l" no lugar de "i" — poucos caracteres.
    ocr = "A hist0ria do documentو antigo"
    fix = "A historia do documento antigo"
    out = apply_correction_policy(ocr, fix, ocr_confidence=0.5, max_divergence=0.35)
    assert out.replaced is True, f"divergência {out.divergence} deveria ser aceita"
    assert out.text == fix
    assert out.flagged is False


def test_ca3_divergencia_alta_nao_reescreve_e_marca():
    from pdf2latex.engines.ocr_vision import apply_correction_policy
    ocr = "fragmento ilegivel xyz"
    # LLM "inventa" um parágrafo plausível e totalmente diferente:
    halluc = "Era uma vez um reino distante onde todos viviam felizes para sempre."
    out = apply_correction_policy(ocr, halluc, ocr_confidence=0.5, max_divergence=0.35)
    assert out.replaced is False, "reescrita divergente JAMAIS deve ser aplicada"
    assert out.flagged is True
    assert out.text == ocr  # mantém o que o OCR realmente leu
    assert out.divergence > 0.35


# ── CA-4: orquestração de uma página ─────────────────────────────────

def test_ca4_process_page_roda_pipeline_e_aplica_politica():
    pre = _FakePreprocessor()
    sig = _FakeSignatureRemover()
    ocr = _FakeOCR(text="linha do ocr", conf=0.8)
    corr = _FakeCorrector("linha do ocr")  # idêntico → sem reescrita
    e = _engine(preprocessor=pre, signature_remover=sig, ocr=ocr, corrector=corr)
    r = e.process_page("imagem_crua", context="contexto", page=3)
    assert pre.called and sig.called
    assert r["text"] == "linha do ocr"
    assert r["confidence"] == 0.8
    assert corr.last_context == "contexto"


def test_ca4_process_page_reescrita_divergente_vira_flag():
    e = _engine(
        ocr=_FakeOCR(text="abc ilegivel", conf=0.4),
        corrector=_FakeCorrector("Um texto completamente diferente e inventado aqui."),
    )
    r = e.process_page("img", page=1)
    assert r["flagged"] is True
    assert r["text"] == "abc ilegivel"  # fidelidade
    assert r["flag"] is not None and r["flag"]["page"] == 1
    assert "revis" in r["flag"]["reason"].lower()


# ── CA-5 / CA-6: convert ─────────────────────────────────────────────

def test_ca5_convert_agrega_paginas_e_flags():
    e = _engine(
        page_loader=_FakePageLoader(n_pages=2),
        ocr=_FakeOCR(text="pagina", conf=0.6),
        corrector=_FakeCorrector("Reescrita totalmente diferente inventada pelo modelo."),
    )
    result = e.convert(Path("/qualquer/doc.pdf"))
    assert result.engine_used == "ocr-vision"
    assert result.confidence == pytest.approx(0.6)
    # Duas páginas, ambas com reescrita divergente → 2 flags, texto = OCR.
    flags = result.structure.get("ocr_review_flags", [])
    assert len(flags) == 2
    assert "pagina" in result.text_content
    assert result.metadata.get("flagged_regions") == 2


def test_ca6_convert_indisponivel_levanta():
    e = _engine()  # sem injeção, sem deps → indisponível
    if e.is_available():
        pytest.skip("ambiente tem opencv+paddleocr; branch de indisponível não aplicável")
    with pytest.raises(RuntimeError):
        e.convert(Path("/qualquer/doc.pdf"))


# ── CA-7: não escolhido por best() quando indisponível ───────────────

def test_ca7_best_nao_escolhe_ocr_vision_indisponivel():
    from pdf2latex.engine_registry import _registry
    best = _registry.best()
    # builtin está sempre disponível; ocr-vision (indisponível) não deve vencer.
    if best is not None:
        assert best.name != "ocr-vision"
