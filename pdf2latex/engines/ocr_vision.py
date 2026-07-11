"""
Engine ocr-vision — OCR de documentos antigos com correção contextual fiel.

Pipeline (SPEC-1001):
    Imagem → OpenCV (deskew/denoise/binariza)
           → remoção de assinatura
           → PaddleOCR (texto + confiança)
           → Vision LLM (correção contextual — SUGERE, não reescreve cego)
           → texto final + regiões marcadas para revisão

Princípio inegociável: FIDELIDADE > FLUÊNCIA. A correção do Vision LLM é uma
sugestão; reescritas divergentes NUNCA são aplicadas — são mantidas como
estavam no OCR e marcadas para revisão humana. Coerente com a política
anti-overclaim do ecossistema (CORRIGENDUM.md / metacognitive_evaluator).

As dependências reais (opencv-python, paddleocr, pdf2image, modelo de visão)
são opcionais e carregadas sob demanda. Todos os componentes podem ser
injetados (injeção de dependência), o que torna o engine testável sem elas.
"""

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .base import BaseEngine, ConversionResult
from ..engine_registry import register_engine


# ── Política de correção (núcleo da fidelidade) ──────────────────────

@dataclass
class CorrectionOutcome:
    """Resultado da política de correção para um trecho de texto."""
    text: str          # texto final adotado
    replaced: bool     # True se a sugestão do LLM foi aceita
    flagged: bool      # True se marcado para revisão humana
    divergence: float  # 0.0 (idêntico) a 1.0 (totalmente diferente)
    reason: str


def apply_correction_policy(
    ocr_text: str,
    suggestion: Optional[str],
    *,
    ocr_confidence: float = 0.5,
    max_divergence: float = 0.35,
) -> CorrectionOutcome:
    """Decide se a sugestão do Vision LLM deve ser aceita.

    Função PURA (só stdlib). Regra:
      - sugestão vazia/idêntica → mantém o OCR;
      - divergência baixa (≤ max_divergence, típica de typo de OCR) → aceita;
      - divergência alta (reescrita) → NUNCA aplica; mantém o OCR e marca
        para revisão humana.

    `ocr_confidence` fica disponível para políticas futuras (ex.: ser mais
    tolerante quando o OCR é claramente ruim), sem afetar a garantia de que
    reescritas divergentes jamais são aplicadas silenciosamente.
    """
    ocr_text = ocr_text or ""
    if not suggestion or not suggestion.strip():
        return CorrectionOutcome(ocr_text, False, False, 0.0, "sem sugestão")

    divergence = 1.0 - SequenceMatcher(None, ocr_text, suggestion).ratio()

    if divergence == 0.0:
        return CorrectionOutcome(ocr_text, False, False, 0.0, "idêntico ao OCR")

    if divergence <= max_divergence:
        return CorrectionOutcome(
            suggestion, True, False, divergence,
            "correção aceita (divergência baixa — nível typo)",
        )

    return CorrectionOutcome(
        ocr_text, False, True, divergence,
        "divergência alta — mantido OCR, marcado para revisão humana",
    )


# ── Engine ───────────────────────────────────────────────────────────

class OcrVisionEngine(BaseEngine):
    """Engine opcional para documentos antigos/escaneados.

    Componentes injetáveis (duck typing):
      - preprocessor.process(image) -> image
      - signature_remover.remove(image) -> image
      - ocr.read(image) -> (text, confidence)
      - corrector.suggest(ocr_text, context="") -> suggestion
      - page_loader.load(pdf_path) -> List[image]
    """

    name = "ocr-vision"
    description = (
        "OpenCV (deskew/denoise/binariza) + remoção de assinatura + PaddleOCR "
        "+ correção contextual por Vision LLM que SUGERE e marca confiança, "
        "nunca reescreve cego. Para documentos antigos/escaneados."
    )
    requires_gpu = False
    requires_api_key = False
    min_ram_mb = 2048

    def __init__(
        self,
        *,
        preprocessor=None,
        signature_remover=None,
        ocr=None,
        corrector=None,
        page_loader=None,
        max_divergence: float = 0.35,
    ):
        self._preprocessor = preprocessor
        self._signature_remover = signature_remover
        self._ocr = ocr
        self._corrector = corrector
        self._page_loader = page_loader
        self.max_divergence = max_divergence

    # -- disponibilidade -----------------------------------------------

    def is_available(self) -> bool:
        """Disponível se os componentes forem injetados OU se opencv+paddleocr
        importarem. Degrada graciosamente (False) quando faltam deps."""
        if self._ocr is not None:
            return True
        try:
            import cv2  # noqa: F401
            import paddleocr  # noqa: F401
            return True
        except Exception:
            return False

    # -- pipeline por página -------------------------------------------

    def _run_ocr(self, image) -> Tuple[str, float]:
        if self._ocr is not None:
            return self._ocr.read(image)
        # Caminho real (lazy). Não coberto por teste sem PaddleOCR.
        from paddleocr import PaddleOCR  # pragma: no cover
        engine = PaddleOCR(use_angle_cls=True, lang="pt")  # pragma: no cover
        raw = engine.ocr(image)  # pragma: no cover
        lines, confs = [], []  # pragma: no cover
        for block in (raw or []):  # pragma: no cover
            for _box, (txt, conf) in block:  # pragma: no cover
                lines.append(txt)  # pragma: no cover
                confs.append(float(conf))  # pragma: no cover
        text = "\n".join(lines)  # pragma: no cover
        confidence = sum(confs) / len(confs) if confs else 0.0  # pragma: no cover
        return text, confidence  # pragma: no cover

    def process_page(self, image, *, context: str = "", page: int = 0) -> Dict:
        """Processa UMA página (imagem já carregada) e aplica a política de
        correção. Retorna dict com texto final, confiança e eventual flag."""
        img = image
        if self._preprocessor is not None:
            img = self._preprocessor.process(img)
        if self._signature_remover is not None:
            img = self._signature_remover.remove(img)

        ocr_text, ocr_conf = self._run_ocr(img)

        suggestion = ""
        if self._corrector is not None:
            suggestion = self._corrector.suggest(ocr_text, context=context) or ""

        outcome = apply_correction_policy(
            ocr_text, suggestion,
            ocr_confidence=ocr_conf, max_divergence=self.max_divergence,
        )

        flag = None
        if outcome.flagged:
            flag = {
                "page": page,
                "ocr": ocr_text,
                "suggestion": suggestion,
                "divergence": round(outcome.divergence, 3),
                "reason": outcome.reason,
            }

        return {
            "text": outcome.text,
            "confidence": ocr_conf,
            "replaced": outcome.replaced,
            "flagged": outcome.flagged,
            "flag": flag,
        }

    # -- conversão completa --------------------------------------------

    def _load_pages(self, pdf_path: Path) -> List:
        if self._page_loader is not None:
            return self._page_loader.load(pdf_path)
        from pdf2image import convert_from_path  # pragma: no cover
        return convert_from_path(str(pdf_path))  # pragma: no cover

    def convert(self, pdf_path: Path, **kwargs) -> ConversionResult:
        if not self.is_available():
            raise RuntimeError(
                "Engine 'ocr-vision' indisponível: requer opencv-python + "
                "paddleocr + pdf2image (+ um modelo de visão para correção). "
                "Instale-os ou use --engine builtin."
            )

        pdf_path = Path(pdf_path)
        pages = self._load_pages(pdf_path)

        texts: List[str] = []
        confs: List[float] = []
        flags: List[Dict] = []
        for i, image in enumerate(pages):
            r = self.process_page(image, page=i)
            texts.append(r["text"])
            confs.append(r["confidence"])
            if r["flag"] is not None:
                flags.append(r["flag"])

        text_content = "\n\n".join(texts)
        confidence = sum(confs) / len(confs) if confs else 0.0
        structure = {
            "chapters": [],
            "sections": [],
            "paragraphs": [],
            "special": [],
            "ocr_review_flags": flags,
        }
        metadata = {
            "engine": self.name,
            "pages": len(pages),
            "flagged_regions": len(flags),
            "title": pdf_path.stem,
        }
        return ConversionResult(
            text_content=text_content,
            structure=structure,
            metadata=metadata,
            engine_used=self.name,
            confidence=confidence,
        )


# Auto-registro
register_engine(OcrVisionEngine())
