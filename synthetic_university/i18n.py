"""Internacionalizacao (i18n) — SPEC-935 R85.

Suporte a mensagens em ingles (en_US) e portugues brasileiro (pt_BR)
para todo o pipeline de descoberta interdisciplinar.
"""

from __future__ import annotations
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# =========================================================================
# Catalogo de Traducoes
# =========================================================================

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en_US": {
        # Validation
        "validation.score_empirico": "Empirical Score",
        "validation.relevancia": "Relevance",
        "validation.viability": "Viability",
        "validation.convergencia": "Convergence Rate",
        "validation.endosso": "Endorsement",
        "validation.n_theses": "{n} theses evaluated",
        "validation.n_avaliacoes": "{n} evaluations by professors",
        "validation.pool_profs": "Faculty pool: {n} professors",
        
        # Report headers
        "report.validation_header": "CALIBRATED EMPIRICAL VALIDATION REPORT",
        "report.benchmark_header": "BENCHMARK: REFINED PIPELINE vs. BASELINES",
        "report.discovery_header": "INTERDISCIPLINARY DISCOVERY REPORT",
        
        # Scores
        "score.composite": "Composite Score",
        "score.coherence": "Coherence",
        "score.novelty": "Novelty",
        "score.impact": "Impact",
        "score.viability": "Viability",
        
        # Endorsement levels
        "endorsement.strong": "Strong",
        "endorsement.moderate": "Moderate",
        "endorsement.weak": "Weak",
        
        # Pipeline stages
        "pipeline.generating": "Generating interdisciplinary combinations...",
        "pipeline.validating": "Validating theses with expert panel...",
        "pipeline.embedding": "Building neural embeddings...",
        "pipeline.complete": "Pipeline complete in {time:.1f}s",
        
        # Errors
        "error.no_professors": "No relevant professors found for this thesis",
        "error.embedding_failed": "Failed to compute embedding for '{concept}'",
        
        # Summary
        "summary.total_combinations": "Total combinations: {n}",
        "summary.total_theses": "Total theses: {n}",
        "summary.avg_coherence": "Mean coherence: {v:.4f}",
        "summary.avg_composite": "Mean composite: {v:.4f}",
    },
    "pt_BR": {
        # Validation
        "validation.score_empirico": "Score Empírico",
        "validation.relevancia": "Relevância",
        "validation.viability": "Viability",
        "validation.convergencia": "Taxa de Convergência",
        "validation.endosso": "Endosso",
        "validation.n_theses": "{n} teses avaliadas",
        "validation.n_avaliacoes": "{n} avaliações de professores",
        "validation.pool_profs": "Pool de {n} professores",
        
        # Report headers
        "report.validation_header": "RELATÓRIO DE VALIDAÇÃO EMPÍRICA CALIBRADA",
        "report.benchmark_header": "BENCHMARK: PIPELINE REFINADO vs. BASELINES",
        "report.discovery_header": "RELATÓRIO DE DESCOBERTA INTERDISCIPLINAR",
        
        # Scores
        "score.composite": "Score Composto",
        "score.coherence": "Coerência",
        "score.novelty": "Novidade",
        "score.impact": "Impacto",
        "score.viability": "Viabilidade",
        
        # Endorsement levels
        "endorsement.strong": "Forte",
        "endorsement.moderate": "Moderado",
        "endorsement.weak": "Fraco",
        
        # Pipeline stages
        "pipeline.generating": "Gerando combinações interdisciplinares...",
        "pipeline.validating": "Validando teses com painel de especialistas...",
        "pipeline.embedding": "Construindo embeddings neurais...",
        "pipeline.complete": "Pipeline concluído em {time:.1f}s",
        
        # Errors
        "error.no_professors": "Nenhum professor relevante encontrado para esta tese",
        "error.embedding_failed": "Falha ao computar embedding para '{concept}'",
        
        # Summary
        "summary.total_combinations": "Total de combinações: {n}",
        "summary.total_theses": "Total de teses: {n}",
        "summary.avg_coherence": "Coerência média: {v:.4f}",
        "summary.avg_composite": "Composite médio: {v:.4f}",
    },
}

# Locale padrao
DEFAULT_LOCALE = "en_US"
SUPPORTED_LOCALES = {"en_US", "pt_BR"}


class I18n:
    """Sistema de internacionalizacao.
    
    Uso:
        i18n = I18n(locale='en_US')
        msg = i18n.get('validation.score_empirico')
        msg = i18n.get('validation.n_theses', n=10)
    """
    
    def __init__(self, locale: Optional[str] = None):
        self._translations = TRANSLATIONS
        
        # Detectar locale
        if locale is None:
            locale = self._detect_locale()
        
        # Validar
        if locale not in SUPPORTED_LOCALES:
            logger.warning(f"Locale '{locale}' nao suportado. Usando {DEFAULT_LOCALE}")
            locale = DEFAULT_LOCALE
        
        self.locale = locale
    
    def _detect_locale(self) -> str:
        """Tenta detectar locale do ambiente."""
        import os
        env_locale = os.environ.get("LANG", "").lower()
        if "pt_br" in env_locale or "pt-br" in env_locale:
            return "pt_BR"
        return DEFAULT_LOCALE
    
    def get(self, key: str, **kwargs) -> str:
        """Retorna mensagem traduzida, com format opcional."""
        translations = self._translations.get(self.locale, {})
        msg = translations.get(key, key)  # fallback = propria chave
        
        if kwargs:
            try:
                msg = msg.format(**kwargs)
            except KeyError:
                pass
        
        return msg
    
    def __call__(self, key: str, **kwargs) -> str:
        """Atalho: i18n('key') == i18n.get('key')."""
        return self.get(key, **kwargs)


# Singleton de uso geral
_default_i18n = None

def get_i18n(locale: Optional[str] = None) -> I18n:
    """Retorna instancia singleton de I18n."""
    global _default_i18n
    if _default_i18n is None or locale is not None:
        _default_i18n = I18n(locale=locale)
    return _default_i18n
