"""Orquestrador Principal — Pipeline Completo de Nano-Orquestração.

Coordena 7 fases:
1. Planejamento (NanoPlanner)
2. Especificação (NanoSDD Engine)
3. Escrita (NanoWriter Pool)
4. Verificação (Quality Checker)
5. Coerência Local (CoherenceEngine Pass 1)
6. Coerência Global (CoherenceEngine Pass 2-3)
7. Validação Cruzada (CrossValidator)

Cada fase gera checkpoints. O pipeline é retomável de qualquer checkpoint.
"""

from __future__ import annotations

import json
import logging
import os
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable

from . import (
    COHERENCE_SCORE_TARGET, FIDELITY_THRESHOLD,
    MAX_RETRIES, PARALLEL_WORKERS_DEFAULT,
    Criterion, NanoBlock, NanoPlan,
)
from .planner import NanoPlanner
from .nano_sdd import NanoSDDEngine
from .writer import NanoWriterPool, LiteRTMClient, PoolConfig
from .quality_checker import QualityChecker
from .coherence import CoherenceEngine
from .cross_validator import CrossValidator


logger = logging.getLogger(__name__)

CHECKPOINT_DIR = "checkpoints"


@dataclass
class OrchestrationReport:
    """Relatório completo da orquestração."""
    plan_id: str
    title: str
    total_pages: int
    total_blocks: int
    successful_blocks: int
    failed_blocks: int
    avg_quality_score: float
    coherence_score: float
    cohesion_score: float
    total_time_ms: int
    phases_completed: list[str]
    validation_passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "plan_id": self.plan_id,
            "title": self.title,
            "total_pages": self.total_pages,
            "total_blocks": self.total_blocks,
            "successful_blocks": self.successful_blocks,
            "failed_blocks": self.failed_blocks,
            "avg_quality_score": self.avg_quality_score,
            "coherence_score": self.coherence_score,
            "cohesion_score": self.cohesion_score,
            "total_time_ms": self.total_time_ms,
            "phases_completed": self.phases_completed,
            "validation_passed": self.validation_passed,
            "errors": self.errors,
            "warnings": self.warnings,
        }


class NanoOrchestrator:
    """Orquestrador principal do pipeline de nano-orquestração.

    Uso:
        orchestrator = NanoOrchestrator()
        report = orchestrator.run(
            title="Meu Manuscrito",
            sections=[("Introdução", 5), ...],
        )
    """

    PHASES = [
        "planning",
        "specification",
        "writing",
        "verification",
        "coherence_local",
        "coherence_global",
        "cross_validation",
    ]

    def __init__(self, client: Optional[LiteRTMClient] = None,
                 pool_config: Optional[PoolConfig] = None,
                 checkpoint_dir: str = CHECKPOINT_DIR,
                 dry_run: bool = False):
        self.client = client or LiteRTMClient()
        pool_config = pool_config or PoolConfig()
        pool_config.dry_run = dry_run

        # Componentes
        self.planner = NanoPlanner()
        self.sdd_engine = NanoSDDEngine()
        self.writer_pool = NanoWriterPool(self.client, pool_config)
        self.quality_checker = QualityChecker(self.client)
        self.coherence_engine = CoherenceEngine()
        self.cross_validator = CrossValidator()

        self.checkpoint_dir = checkpoint_dir
        self.dry_run = dry_run
        self._plan: Optional[NanoPlan] = None
        self._phases_completed: list[str] = []
        self._errors: list[str] = []
        self._warnings: list[str] = []
        self._start_time: float = 0.0

    def run(self, title: str, sections: list[tuple[str, int]],
            total_pages: Optional[int] = None,
            from_checkpoint: Optional[str] = None) -> OrchestrationReport:
        """Executa o pipeline completo de nano-orquestração.

        Args:
            title: Título do manuscrito.
            sections: Lista de (nome_seção, páginas).
            total_pages: Total de páginas (calculado se None).
            from_checkpoint: Retomar de checkpoint específico.

        Returns:
            OrchestrationReport com resultados.
        """
        self._start_time = time.time()
        self._phases_completed = []
        self._errors = []

        logger.info(f"=== Iniciando Nano-Orquestração: {title} ===")
        logger.info(f"Seções: {[s for s, _ in sections]}")
        logger.info(f"Páginas: {total_pages or sum(p for _, p in sections)}")

        try:
            # Fase 1: Planejamento
            self._phase_planning(title, sections, total_pages)
            self._save_checkpoint("planning")

            # Fase 2: Especificação
            self._phase_specification()
            self._save_checkpoint("specification")

            # Fase 3: Escrita
            self._phase_writing()
            self._save_checkpoint("writing")

            # Fase 4: Verificação
            self._phase_verification()
            self._save_checkpoint("verification")

            # Fase 5: Coerência Local (Pass 1)
            self._phase_coherence_local()
            self._save_checkpoint("coherence_local")

            # Fase 6: Coerência Global (Pass 2-3)
            self._phase_coherence_global()
            self._save_checkpoint("coherence_global")

            # Fase 7: Validação Cruzada
            validation = self._phase_cross_validation()
            self._save_checkpoint("cross_validation")

        except Exception as e:
            logger.error(f"Erro fatal na orquestração: {e}")
            logger.error(traceback.format_exc())
            self._errors.append(f"Fatal: {str(e)[:500]}")

        # Relatório final
        report = self._build_report()
        logger.info(f"=== Orquestração concluída em {report.total_time_ms}ms ===")
        logger.info(f"Status: {'APROVADO' if report.validation_passed else 'REPROVADO'}")
        return report

    def _phase_planning(self, title: str, sections: list[tuple[str, int]],
                         total_pages: Optional[int]):
        """Fase 1: Planejamento da decomposição."""
        logger.info("Fase 1/7: Planejamento")
        self._plan = self.planner.plan(title, sections, total_pages)
        val = self.planner.validate_plan(self._plan)

        if not val["valid"]:
            for err in val["errors"]:
                self._errors.append(f"Planejamento: {err}")
                logger.warning(f"Planejamento: {err}")

        logger.info(f"Plano: {self._plan.total_blocks} blocos, "
                     f"{self._plan.estimated_total_tokens} tokens estimados")

    def _phase_specification(self):
        """Fase 2: Geração de especificações para cada bloco."""
        logger.info("Fase 2/7: Especificação (NanoSDD)")
        assert self._plan is not None, "Plano não criado"

        self._plan = self.sdd_engine.apply_criteria_to_plan(self._plan)
        coverage = self.sdd_engine.validate_criteria_coverage(self._plan)

        if not coverage["valid"]:
            self._errors.append(f"SDD: {coverage['blocks_without_criteria']} blocos sem critérios")

        logger.info(f"Critérios: {coverage['total_criteria']} total, "
                     f"média {coverage['avg_criteria_per_block']}/bloco")

    def _phase_writing(self):
        """Fase 3: Escrita paralela dos nanoblocos."""
        logger.info("Fase 3/7: Escrita")
        assert self._plan is not None, "Plano não criado"

        if self.dry_run:
            logger.info("Modo dry-run: simulando escrita...")

        blocks = self.writer_pool.write_blocks_batch(
            self._plan.blocks, self._plan
        )
        self._plan.blocks = blocks

        successful = sum(1 for b in blocks if b.status == "written")
        failed = sum(1 for b in blocks if b.status == "failed")

        if failed > 0:
            self._errors.append(f"Escrita: {failed} blocos falharam")
            for b in blocks:
                if b.status == "failed":
                    self._warnings.append(f"Bloco {b.index}: {b.error[:100]}")

        logger.info(f"Escrita: {successful} ok, {failed} falhas")

        # Estatísticas do pool
        pool_stats = self.writer_pool.get_stats()
        logger.info(f"Pool: {pool_stats['total_calls']} chamadas, "
                     f"{pool_stats['fallbacks_used']} fallbacks")

    def _phase_verification(self):
        """Fase 4: Verificação de qualidade."""
        logger.info("Fase 4/7: Verificação de Qualidade")
        assert self._plan is not None, "Plano não criado"

        total_score = 0.0
        verified_count = 0

        for block in self._plan.blocks:
            if block.status != "written":
                continue

            block, report = self.quality_checker.verify_and_fix(block, self._plan)
            total_score += block.quality_score
            verified_count += 1

            if not report.passed:
                self._warnings.append(
                    f"Qualidade bloco {block.index}: score {report.score}"
                )

        avg_score = total_score / max(verified_count, 1)
        logger.info(f"Qualidade média: {avg_score:.2f}/10 ({verified_count} blocos)")

    def _phase_coherence_local(self):
        """Fase 5: Coerência Local (Pass 1)."""
        logger.info("Fase 5/7: Coerência Local (Pass 1)")
        assert self._plan is not None, "Plano não criado"

        self._plan, scores = self.coherence_engine.apply_all(self._plan)
        logger.info(f"Score coerência: {scores['composite']}/10")

    def _phase_coherence_global(self):
        """Fase 6: Coerência Global já incluída no Pass 2-3."""
        logger.info("Fase 6/7: Coerência Global (completa via Pass 2-3)")
        # Já executada na fase 5 via apply_all

    def _phase_cross_validation(self) -> dict:
        """Fase 7: Validação Cruzada final.

        Returns:
            Dict com resultados da validação.
        """
        logger.info("Fase 7/7: Validação Cruzada")
        assert self._plan is not None, "Plano não criado"

        report = self.cross_validator.validate_all(self._plan)

        if not report.passed:
            self._errors.append(
                f"Validação: coesão {report.cohesion_score}/{COHERENCE_SCORE_TARGET}"
            )

        logger.info(
            f"Validação: {report.smooth_transitions}/{report.validated_pairs} "
            f"transições suaves, "
            f"{report.contradictions} contradições, "
            f"coesão {report.cohesion_score}"
        )

        return {
            "cohesion_score": report.cohesion_score,
            "smooth_transitions": report.smooth_transitions,
            "contradictions": report.contradictions,
            "passed": report.passed,
        }

    def _build_report(self) -> OrchestrationReport:
        """Constrói relatório final."""
        assert self._plan is not None, "Plano não criado"

        successful = sum(1 for b in self._plan.blocks if b.status in ("written", "verified"))
        failed = sum(1 for b in self._plan.blocks if b.status == "failed")
        scores = [b.quality_score for b in self._plan.blocks if b.quality_score > 0]
        avg_quality = sum(scores) / max(len(scores), 1)

        coherence_scores = self.coherence_engine.get_scores()
        validation = self.cross_validator.calculate_cohesion_score(self._plan)

        return OrchestrationReport(
            plan_id=self._plan.id,
            title=self._plan.title,
            total_pages=self._plan.total_pages,
            total_blocks=self._plan.total_blocks,
            successful_blocks=successful,
            failed_blocks=failed,
            avg_quality_score=round(avg_quality, 2),
            coherence_score=coherence_scores.get("composite", 0.0),
            cohesion_score=validation,
            total_time_ms=int((time.time() - self._start_time) * 1000),
            phases_completed=list(self._phases_completed),
            validation_passed=validation >= COHERENCE_SCORE_TARGET,
            errors=self._errors,
            warnings=self._warnings,
        )

    def _save_checkpoint(self, phase: str):
        """Salva checkpoint para retomada."""
        self._phases_completed.append(phase)
        if self.dry_run:
            return

        os.makedirs(self.checkpoint_dir, exist_ok=True)
        assert self._plan is not None, "Plano não criado"

        checkpoint = {
            "phase": phase,
            "timestamp": datetime.now().isoformat(),
            "phases_completed": list(self._phases_completed),
            "plan": self._plan.to_dict(),
            "pool_stats": self.writer_pool.get_stats(),
        }

        path = os.path.join(
            self.checkpoint_dir,
            f"checkpoint_{self._plan.id}_{phase}.json"
        )
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            logger.info(f"Checkpoint salvo: {path}")
        except Exception as e:
            logger.warning(f"Não foi possível salvar checkpoint: {e}")

    def load_checkpoint(self, checkpoint_path: str) -> Optional[str]:
        """Carrega checkpoint e retorna última fase concluída.

        Args:
            checkpoint_path: Caminho para o arquivo de checkpoint.

        Returns:
            Nome da última fase concluída ou None.
        """
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Falha ao carregar checkpoint: {e}")
            return None

        # Restaura plano
        plan_data = data.get("plan", {})
        blocks = []
        for bd in plan_data.get("blocks", []):
            block = NanoBlock(**{k: v for k, v in bd.items()
                                  if k in NanoBlock.__dataclass_fields__})
            block.criteria = [Criterion(**c) for c in bd.get("criteria", [])]
            blocks.append(block)

        self._plan = NanoPlan(
            id=plan_data.get("id", ""),
            title=plan_data.get("title", ""),
            total_pages=plan_data.get("total_pages", 0),
            total_blocks=plan_data.get("total_blocks", 0),
            sections=plan_data.get("sections", []),
            estimated_total_tokens=plan_data.get("estimated_total_tokens", 0),
            created_at=plan_data.get("created_at", 0),
            metadata=plan_data.get("metadata", {}),
            blocks=blocks,
        )

        self._phases_completed = data.get("phases_completed", [])
        logger.info(f"Checkpoint carregado: {data.get('phase')}, "
                     f"fases: {self._phases_completed}")

        return data.get("phase")

    def get_plan_preview(self) -> dict:
        """Retorna preview do plano (se existir)."""
        if not self._plan:
            return {}
        return {
            "id": self._plan.id,
            "title": self._plan.title,
            "total_pages": self._plan.total_pages,
            "total_blocks": self._plan.total_blocks,
            "sections": self._plan.sections,
            "phases_completed": list(self._phases_completed),
        }
