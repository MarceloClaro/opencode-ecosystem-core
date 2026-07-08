# -*- coding: utf-8 -*-
"""
SDD Engine — Specification-Driven Development
=============================================
Motor de especificações do ecossistema. Implementa:

1. `Specification`: especificação executável com critérios de aceitação
   verificáveis (funções booleanas) e invariantes.
2. `SpecRegistry`: registro central que carrega as specs formais de `specs/*.md`
   (frontmatter YAML) e as specs dinâmicas criadas em tempo de execução.
3. `SpecVerifier`: verificador que valida entregas contra critérios de
   aceitação ANTES de qualquer `task.complete` (modo estrito).

Fluxo SDD: ESPECIFICAR → RED → GREEN → REFACTOR → VERIFICAR

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import os
import re
import glob
import uuid
import logging
from typing import Dict, List, Any, Callable, Optional

from mci.metabus import metabus

logger = logging.getLogger("sdd-engine")
logger.setLevel(logging.INFO)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPECS_DIR = os.path.join(REPO_ROOT, "specs")


class AcceptanceCriterion:
    """Critério de aceitação verificável programaticamente (TDD-friendly)."""

    def __init__(self, criterion_id: str, description: str,
                 check_fn: Optional[Callable[[Any], bool]] = None):
        self.criterion_id = criterion_id
        self.description = description
        # check_fn recebe a entrega (output) e retorna True/False
        self.check_fn = check_fn or (lambda output: bool(output))

    def check(self, output: Any) -> bool:
        try:
            return bool(self.check_fn(output))
        except Exception as e:
            logger.warning(f"Critério {self.criterion_id} lançou exceção: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {"criterion_id": self.criterion_id, "description": self.description}


class Specification:
    """Especificação executável de uma tarefa ou componente (SDD)."""

    def __init__(self, spec_id: str, title: str, objective: str,
                 criteria: Optional[List[AcceptanceCriterion]] = None,
                 invariants: Optional[List[str]] = None,
                 non_goals: Optional[List[str]] = None,
                 component: str = "", test_file: str = ""):
        self.spec_id = spec_id
        self.title = title
        self.objective = objective
        self.criteria = criteria or []
        self.invariants = invariants or []
        self.non_goals = non_goals or []
        self.component = component
        self.test_file = test_file
        self.status = "draft"  # draft -> red -> green -> verified

    def add_criterion(self, description: str,
                      check_fn: Optional[Callable[[Any], bool]] = None) -> AcceptanceCriterion:
        criterion = AcceptanceCriterion(
            f"{self.spec_id}-AC{len(self.criteria) + 1}", description, check_fn
        )
        self.criteria.append(criterion)
        return criterion

    def to_dict(self) -> Dict[str, Any]:
        return {
            "spec_id": self.spec_id,
            "title": self.title,
            "objective": self.objective,
            "component": self.component,
            "test_file": self.test_file,
            "status": self.status,
            "criteria": [c.to_dict() for c in self.criteria],
            "invariants": self.invariants,
            "non_goals": self.non_goals,
        }


def _parse_spec_frontmatter(content: str) -> Dict[str, str]:
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    meta: Dict[str, str] = {}
    if match:
        for line in match.group(1).splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
    return meta


class SpecRegistry:
    """Registro central de especificações (formais + dinâmicas)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpecRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.specs: Dict[str, Specification] = {}
        self._initialized = True
        self.load_formal_specs()

    def load_formal_specs(self, specs_dir: str = SPECS_DIR) -> int:
        """Carrega as especificações formais de specs/*.md."""
        count = 0
        for path in sorted(glob.glob(os.path.join(specs_dir, "SPEC-*.md"))):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                meta = _parse_spec_frontmatter(content)
                spec_id = meta.get("spec_id")
                if not spec_id:
                    continue
                spec = Specification(
                    spec_id=spec_id,
                    title=meta.get("title", ""),
                    objective=f"Especificação formal do componente {meta.get('component', '')}",
                    component=meta.get("component", ""),
                    test_file=meta.get("test_file", ""),
                )
                spec.status = meta.get("status", "draft")
                self.specs[spec_id] = spec
                metabus.publish_subsystem_event(
                    "sdd",
                    "spec.loaded",
                    {"spec_id": spec_id, "title": spec.title, "status": spec.status},
                    source_agent="spec_registry",
                )
                count += 1
            except Exception as e:
                logger.error(f"Erro ao carregar spec {path}: {e}")
        logger.info(f"{count} especificações formais carregadas.")
        return count

    def create_task_spec(self, title: str, objective: str,
                         criteria_descriptions: Optional[List[str]] = None) -> Specification:
        """Cria uma especificação dinâmica para uma tarefa (usada pelos agentes)."""
        spec_id = f"TSPEC-{uuid.uuid4().hex[:8]}"
        spec = Specification(spec_id, title, objective)
        for desc in (criteria_descriptions or []):
            spec.add_criterion(desc)
        spec.status = "red"  # nasce em RED: critérios definidos, entrega ainda ausente
        self.specs[spec_id] = spec
        metabus.publish_subsystem_event(
            "sdd",
            "spec.created",
            {"spec_id": spec_id, "title": title, "criteria_count": len(spec.criteria)},
            source_agent="spec_registry",
        )
        metabus.memory.upsert_semantic_topic(
            "sdd.specs",
            lesson=f"Spec dinâmica criada: {spec_id} ({title}).",
            metadata={"last_spec_id": spec_id},
        )
        return spec

    def get(self, spec_id: str) -> Optional[Specification]:
        return self.specs.get(spec_id)

    def coverage_report(self) -> Dict[str, Any]:
        """Relatório de cobertura: quais componentes têm spec e teste vinculados."""
        return {
            "total_specs": len(self.specs),
            "formal": [s.to_dict() for s in self.specs.values() if s.spec_id.startswith("SPEC-")],
            "dynamic": [s.to_dict() for s in self.specs.values() if s.spec_id.startswith("TSPEC-")],
        }


class SpecVerifier:
    """
    Verificador SDD/TDD: valida entregas contra os critérios de aceitação.
    Implementa a transição RED → GREEN do ciclo TDD.
    """

    def __init__(self, registry: Optional[SpecRegistry] = None):
        self.registry = registry or SpecRegistry()

    def verify(self, spec_id: str, output: Any) -> Dict[str, Any]:
        """Executa todos os critérios da spec contra a entrega."""
        spec = self.registry.get(spec_id)
        if spec is None:
            return {"spec_id": spec_id, "verified": False,
                    "error": "Especificação não encontrada."}

        results = []
        for criterion in spec.criteria:
            passed = criterion.check(output)
            results.append({
                "criterion_id": criterion.criterion_id,
                "description": criterion.description,
                "passed": passed,
            })

        all_passed = all(r["passed"] for r in results) if results else False
        spec.status = "green" if all_passed else "red"

        result = {
            "spec_id": spec_id,
            "verified": all_passed,
            "status": spec.status,
            "criteria_results": results,
            "passed_count": sum(1 for r in results if r["passed"]),
            "total_count": len(results),
        }
        metabus.publish_subsystem_event(
            "sdd",
            "spec.verified",
            {
                "spec_id": spec_id,
                "verified": all_passed,
                "passed_count": result["passed_count"],
                "total_count": result["total_count"],
            },
            source_agent="spec_verifier",
        )
        metabus.memory.update_topic_confidence("sdd", 1.0 if all_passed else 0.4)
        return result


# Singletons globais
spec_registry = SpecRegistry()
spec_verifier = SpecVerifier(spec_registry)
