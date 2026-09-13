# Research Factory — SPEC-935-R471 (M1)
#
# Meta-graph de fábrica de pesquisa inspirado no open-swe
# (langchain-ai/open-swe): threads duráveis, entrypoints
# research/review/analyze/chat/schedule e trilha de auditoria
# por etapa. Componentes externos são injetáveis (testes herméticos
# e reuso do pipeline nativo).

from research_factory.analyzer import ReviewStyleAnalyzer
from research_factory.audit import AuditEntry, AuditLog
from research_factory.graph import ResearchFactory
from research_factory.scheduler import ResearchScheduler
from research_factory.threads import ResearchThread, ThreadStore

__all__ = [
    "ResearchFactory",
    "ResearchThread",
    "ThreadStore",
    "AuditEntry",
    "AuditLog",
    "ReviewStyleAnalyzer",
    "ResearchScheduler",
]