"""Orquestrador Central da Universidade Sintética — SPEC-935.

Coordena faculdades, motor combinatorial, correlator, gerador de teses
e grafo de conhecimento em ciclo completo de descoberta.
"""

from __future__ import annotations
import time
import logging
import random
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Callable
from collections import defaultdict

from synthetic_university.faculties import (
    ALL_FACULTIES, FACULTY_MAP, get_faculty, list_all_concepts
)
from synthetic_university.combinatorial_engine import (
    CombinatorialDiscoveryEngine, CombinationResult
)
from synthetic_university.correlator import (
    InterdisciplinaryCorrelator, Correlation, CorrelationType
)
from synthetic_university.thesis_generator import (
    ThesisGenerator, Thesis, AcademicLevel
)
from synthetic_university.knowledge_graph import UniversityKnowledgeGraph
from synthetic_university.curriculum import Curriculum, Discipline
from synthetic_university.agents.professors import (
    create_all_professors, get_professors_by_faculty, PROFESSOR_REGISTRY
)

logger = logging.getLogger(__name__)


@dataclass
class UniversityReport:
    """Relatório completo de um ciclo da universidade sintética."""
    cycle_id: str
    combinations_tested: int
    correlations_found: int
    theses_generated: int
    graph_nodes: int
    graph_edges: int
    top_theses: List[Thesis]
    top_correlations: List[Correlation]
    top_combinations: List[CombinationResult]
    faculty_coverage: Dict[str, int]
    duration_s: float
    stats: Dict


class SyntheticUniversity:
    """Orquestrador central da Universidade Sintética Transversal.
    
    Ciclo operacional:
    1. Carregar faculdades, conceitos e professores
    2. Executar descoberta combinatorial (10k+ combinações)
    3. Descobrir correlações interdisciplinares
    4. Gerar teses PhD-level
    5. Construir grafo de conhecimento
    6. Gerar relatório e publicar eventos
    """
    
    def __init__(self, target_combinations: int = 10000):
        self.target_combinations = target_combinations
        
        # Faculdades
        self.faculties = ALL_FACULTIES
        self.faculty_map = FACULTY_MAP
        
        # Subsistemas
        self.engine = CombinatorialDiscoveryEngine(self.faculty_map)
        self.correlator = InterdisciplinaryCorrelator(self.faculty_map)
        self.thesis_generator = ThesisGenerator()
        self.knowledge_graph = UniversityKnowledgeGraph()
        
        # Professores
        self.professors = create_all_professors()
        
        # Currículo
        self.curriculum = Curriculum()
        
        # Estado
        self.total_cycles = 0
        self.total_combinations_all_cycles = 0
        self.total_theses_all_cycles = 0
        self._reports: List[UniversityReport] = []
        
        # Callbacks para integração MetaBus
        self._event_callbacks: List[Callable] = []
        
        logger.info(f"Universidade Sintética inicializada: "
                     f"{len(self.faculties)} faculdades, "
                     f"{len(self.professors)} professores, "
                     f"target={target_combinations} combinações")
    
    def on_event(self, callback: Callable):
        """Registra callback para eventos (integração MetaBus)."""
        self._event_callbacks.append(callback)
    
    def _emit_event(self, event_type: str, data: dict):
        """Emite evento para callbacks registrados."""
        for cb in self._event_callbacks:
            try:
                cb(event_type, data)
            except Exception as e:
                logger.error(f"Event callback error: {e}")
    
    def run_full_cycle(
        self,
        faculty_ids: Optional[List[str]] = None,
        target_combinations: Optional[int] = None,
        generate_theses: bool = True,
    ) -> UniversityReport:
        """Executa ciclo completo de descoberta universitária.
        
        Args:
            faculty_ids: IDs das faculdades a incluir (None = todas)
            target_combinations: Número alvo de combinações (default = self.target)
            generate_theses: Se deve gerar teses ao final
        
        Returns:
            UniversityReport com resultados do ciclo
        """
        start_time = time.time()
        cycle_id = f"cycle_{self.total_cycles + 1}_{int(start_time)}"
        
        target = target_combinations or self.target_combinations
        
        logger.info(f"=== Ciclo {self.total_cycles + 1}: {target} combinações ===")
        self._emit_event("cycle.start", {
            "cycle_id": cycle_id,
            "target_combinations": target,
        })
        
        # 1. Construir grafo base com faculdades e conceitos
        self.knowledge_graph.build_from_faculties(self.faculties)
        
        # 2. Descoberta combinatorial
        combinations = self.engine.full_discovery_run(
            target_combinations=target,
            faculty_ids=faculty_ids,
        )
        self.total_combinations_all_cycles += len(combinations)
        self._emit_event("combinations.ready", {
            "count": len(combinations),
            "stats": self.engine.get_statistics(),
        })
        
        # 3. Adicionar combinações ao grafo
        self.knowledge_graph.build_from_combinations(combinations)
        
        # 4. Descobrir correlações das melhores combinações
        top_combinations = self.engine.get_top_combinations(200, min_composite=0.4)
        correlations = self.correlator.batch_discover(top_combinations, threshold=0.3)
        self._emit_event("correlations.ready", {
            "count": len(correlations),
            "stats": self.correlator.get_statistics(),
        })
        
        # 5. Adicionar correlações ao grafo
        self.knowledge_graph.build_from_correlations(correlations)
        
        # 6. Gerar teses (opcional)
        theses = []
        if generate_theses and top_combinations:
            theses = self.thesis_generator.batch_generate(
                top_combinations, correlations,
                max_theses=50, min_composite=0.5,
            )
            self.total_theses_all_cycles += len(theses)
            self.knowledge_graph.build_from_theses(theses)
            self._emit_event("theses.ready", {
                "count": len(theses),
                "stats": self.thesis_generator.get_statistics(),
            })
        
        # 7. Atualizar currículo com descobertas
        for thesis in theses[:10]:
            disc = Discipline(
                name=thesis.title[:80],
                faculty=thesis.faculties_involved[0] if thesis.faculties_involved else "interdisciplinary",
                description=thesis.hypothesis[:200],
                concepts=list(thesis.faculties_involved),
                level=thesis.academic_level.value,
            )
            self.curriculum.add_discipline(disc)
        
        # 8. Relatório
        duration = time.time() - start_time
        graph_stats = self.knowledge_graph.get_statistics()
        
        report = UniversityReport(
            cycle_id=cycle_id,
            combinations_tested=self.engine.total_combinations_tested,
            correlations_found=len(correlations),
            theses_generated=len(theses),
            graph_nodes=graph_stats["total_nodes"],
            graph_edges=graph_stats["total_edges"],
            top_theses=self.thesis_generator.get_top_theses(10),
            top_correlations=self.correlator.get_top_correlations(10),
            top_combinations=self.engine.get_top_combinations(20),
            faculty_coverage={
                fac.id: self.engine.get_combinations_by_faculty(fac.id).__len__()
                for fac in self.faculties
            },
            duration_s=round(duration, 2),
            stats={
                "engine": self.engine.get_statistics(),
                "correlator": self.correlator.get_statistics(),
                "thesis": self.thesis_generator.get_statistics(),
                "graph": graph_stats,
            },
        )
        
        self._reports.append(report)
        self.total_cycles += 1
        
        logger.info(
            f"Ciclo {self.total_cycles} concluído em {duration:.1f}s: "
            f"{report.combinations_tested} combinações, "
            f"{report.correlations_found} correlações, "
            f"{report.theses_generated} teses"
        )
        self._emit_event("cycle.complete", {
            "cycle_id": cycle_id,
            "duration_s": duration,
            "report": {
                "combinations": report.combinations_tested,
                "correlations": report.correlations_found,
                "theses": report.theses_generated,
                "graph_nodes": report.graph_nodes,
            },
        })
        
        return report
    
    def get_latest_report(self) -> Optional[UniversityReport]:
        """Retorna o relatório mais recente."""
        return self._reports[-1] if self._reports else None
    
    def get_summary(self) -> Dict:
        """Resumo completo da universidade."""
        return {
            "faculties": len(self.faculties),
            "total_concepts": sum(len(f.conceitos) for f in self.faculties),
            "professors": len(self.professors),
            "cycles_completed": self.total_cycles,
            "total_combinations_tested": self.total_combinations_all_cycles,
            "total_theses_generated": self.total_theses_all_cycles,
            "academic_levels": {
                level.value: self.thesis_generator.get_theses_by_level(level).__len__()
                for level in AcademicLevel
            },
            "graph_statistics": self.knowledge_graph.get_statistics(),
            "latest_cycle_duration_s": (
                self._reports[-1].duration_s if self._reports else 0
            ),
        }
    
    def get_curriculum_vitae(self) -> str:
        """Gera um CV textual da universidade com suas descobertas."""
        lines = [
            "=" * 60,
            "UNIVERSIDADE SINTÉTICA TRANSVERSAL",
            "=" * 60,
            "",
            f"Faculdades: {len(self.faculties)}",
        ]
        for fac in self.faculties:
            lines.append(f"  • {fac.nome} ({fac.nome_en}) — {len(fac.conceitos)} conceitos")
        
        lines += [
            "",
            f"Professores: {len(self.professors)}",
            f"Ciclos completados: {self.total_cycles}",
            f"Combinações testadas: {self.total_combinations_all_cycles}",
            f"Teses geradas: {self.total_theses_all_cycles}",
            "",
        ]
        
        if self._reports:
            latest = self._reports[-1]
            lines += [
                "Último Ciclo:",
                f"  Duração: {latest.duration_s:.1f}s",
                f"  Combinações: {latest.combinations_tested}",
                f"  Correlações: {latest.correlations_found}",
                f"  Teses: {latest.theses_generated}",
                f"  Nós no grafo: {latest.graph_nodes}",
                f"  Arestas no grafo: {latest.graph_edges}",
                "",
                "Top Teses:",
            ]
            for t in latest.top_theses[:5]:
                lines.append(f"  • [{t.academic_level.value}] {t.title[:80]}")
            
            lines += ["", "Top Correlações:"]
            for c in latest.top_correlations[:5]:
                concepts_str = " × ".join(list(c.concepts)[:3])
                lines.append(
                    f"  • {c.correlation_type.value}: {concepts_str} "
                    f"(força={c.strength:.2f}, comp={c.composite_correlation:.2f})"
                )
        
        return "\n".join(lines)
    
    def export_report_json(self) -> Dict:
        """Exporta estado completo para JSON."""
        latest = self.get_latest_report()
        return {
            "summary": self.get_summary(),
            "latest_report": {
                "cycle_id": latest.cycle_id if latest else None,
                "combinations_tested": latest.combinations_tested if latest else 0,
                "correlations_found": latest.correlations_found if latest else 0,
                "theses_generated": latest.theses_generated if latest else 0,
                "graph_nodes": latest.graph_nodes if latest else 0,
                "graph_edges": latest.graph_edges if latest else 0,
                "duration_s": latest.duration_s if latest else 0,
                "top_theses": [
                    {
                        "id": t.thesis_id,
                        "title": t.title,
                        "level": t.academic_level.value,
                        "score": t.composite_score,
                        "faculties": list(t.faculties_involved),
                    }
                    for t in (latest.top_theses if latest else [])
                ],
                "top_correlations": [
                    {
                        "id": c.correlation_id,
                        "concepts": list(c.concepts),
                        "type": c.correlation_type.value,
                        "strength": c.strength,
                        "composite": c.composite_correlation,
                    }
                    for c in (latest.top_correlations if latest else [])
                ],
            } if latest else {},
            "knowledge_graph": self.knowledge_graph.to_dict(),
        }
