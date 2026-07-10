# -*- coding: utf-8 -*-
"""
ARCHE RLT — Reasoning Logic Tree (R114, SPEC-057)
====================================================
Implementação fiel de SPEC-057 (ARCHE Reasoning Logic Tree), que formaliza
os motores de raciocínio do ecossistema (``reasoning/engines.py``) nos
**6 tipos de inferência de Peirce**, compostos em uma árvore lógica
auditável (RLT).

Os 6 tipos de Peirce (ARCHE Benchmark):
  - DR (Deduction-Rule):      regra + caso ⊢ resultado necessário
  - DC (Deduction-Case):      regra + resultado ⊢ caso provável
  - IC (Induction-Common):    casos + resultados ⊢ regra generalizada
  - IH (Induction-Case):      resultado + regra hipotética ⊢ confirmação
  - AK (Abduction-Knowledge): resultado + regra conhecida ⊢ explicação
  - AP (Abduction-Phenomenon):resultado ⊢ nova categoria explicativa

Mapeamento motor → tipo Peirce (Seção 5 da SPEC-057, "Integração com o
Ecossistema": "DR/DC: Z3 verificação formal", "IC/IH: SymPy +
estatística", "AK: miniKanren lógica relacional", "AP: Critical
(falácias + vieses)" — os demais 8 motores são mapeados pela tabela de
taxonomia da Seção 3 conforme sua natureza declarada).

Este módulo é a PRIMEIRA implementação em código de SPEC-057 (que
constava como "SDD Completo" mas sem nenhum arquivo .py correspondente).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from reasoning.engines import ReasoningResult


class PeirceType(Enum):
    """Os 6 tipos formais de inferência de Peirce (ARCHE Benchmark)."""
    DR = "Deduction-Rule"
    DC = "Deduction-Case"
    IC = "Induction-Common"
    IH = "Induction-Case"
    AK = "Abduction-Knowledge"
    AP = "Abduction-Phenomenon"


# Mapeamento motor -> tipo Peirce, seguindo SPEC-057 Secao 3 (taxonomia)
# e Secao 5 (integracao com os motores reais de reasoning/engines.py).
ENGINE_TO_PEIRCE: Dict[str, PeirceType] = {
    "z3": PeirceType.DR,                    # formal/dedutivo -> DR
    "sympy": PeirceType.IC,                 # simbolico/generalizacao -> IC
    "kanren": PeirceType.AK,                # logica relacional -> AK (SPEC-057 Sec.5)
    "critical": PeirceType.AP,              # falacias/vieses -> AP (SPEC-057 Sec.5)
    "bayesian": PeirceType.DC,              # probabilistico/bayesiano -> DC
    "causal": PeirceType.AK,                # explicacao/diagnostico -> AK
    "temporal": PeirceType.IC,              # sequencias/generalizacao -> IC
    "fuzzy": PeirceType.IH,                 # hipotetico-dedutivo/teste -> IH
    "chain_of_thought": PeirceType.DR,      # dedutivo passo-a-passo -> DR
    "analogical": PeirceType.IC,            # indutivo/generalizacao -> IC
    "counterfactual": PeirceType.AP,        # inovacao/emergente -> AP
    "quantum": PeirceType.AP,               # emergente/nao-classico -> AP
}


@dataclass
class RLTNode:
    """Nó da árvore de raciocínio (Reasoning Logic Tree)."""
    inference_type: PeirceType
    premise: str
    conclusion: str
    confidence: float = 0.5
    id: str = field(default_factory=lambda: f"rlt-{uuid.uuid4().hex[:8]}")
    children: List["RLTNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_child(self, child: "RLTNode") -> None:
        self.children.append(child)

    def depth(self) -> int:
        if not self.children:
            return 1
        return 1 + max(c.depth() for c in self.children)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "inference_type": self.inference_type.value,
            "inference_code": self.inference_type.name,
            "premise": self.premise,
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "children": [c.to_dict() for c in self.children],
        }


class ReasoningMapper:
    """Mapeia resultados de motores de raciocínio (``ReasoningResult``)
    para os 6 tipos de inferência de Peirce."""

    def classify(self, result: ReasoningResult) -> PeirceType:
        return ENGINE_TO_PEIRCE.get(result.engine, PeirceType.DR)

    def classify_engine_name(self, engine_name: str) -> PeirceType:
        return ENGINE_TO_PEIRCE.get(engine_name, PeirceType.DR)

    def coverage_report(self) -> Dict[str, Any]:
        """Relatório de cobertura: todos os motores conhecidos mapeados?"""
        from reasoning.engines import MultiReasoningEngine
        known_engines = set(MultiReasoningEngine().engines.keys())
        mapped_engines = set(ENGINE_TO_PEIRCE.keys())
        return {
            "known_engines": sorted(known_engines),
            "mapped_engines": sorted(mapped_engines),
            "unmapped": sorted(known_engines - mapped_engines),
            "coverage_pct": round(
                100.0 * len(known_engines & mapped_engines) / max(1, len(known_engines)), 1
            ),
        }


class RLTBuilder:
    """Constrói uma árvore lógica (RLT) a partir de uma cadeia de
    raciocínio — tipicamente a saída de ``MultiReasoningEngine.ensemble()``."""

    MAX_DEPTH = 10

    def __init__(self, mapper: Optional[ReasoningMapper] = None):
        self.mapper = mapper or ReasoningMapper()

    def build_from_ensemble(self, query: str, ensemble_result: Dict[str, Any]) -> RLTNode:
        """Constrói a raiz da árvore a partir do dict retornado por
        ``MultiReasoningEngine.ensemble(query)``: cada motor que
        respondeu vira um nó-filho classificado por tipo de Peirce."""
        results = ensemble_result.get("results", {})
        best_engine = ensemble_result.get("best_engine")

        root_conclusion = ""
        if best_engine and best_engine in results:
            root_conclusion = results[best_engine].get("conclusion", "")

        root = RLTNode(
            inference_type=PeirceType.DR,
            premise=query,
            conclusion=root_conclusion or "Síntese do ensemble de raciocínio",
            confidence=results.get(best_engine, {}).get("confidence", 0.5) if best_engine else 0.5,
            metadata={"root": True, "best_engine": best_engine},
        )

        for engine_name, result_dict in results.items():
            if not result_dict.get("available", True):
                continue
            peirce_type = self.mapper.classify_engine_name(engine_name)
            child = RLTNode(
                inference_type=peirce_type,
                premise=query,
                conclusion=result_dict.get("conclusion", ""),
                confidence=result_dict.get("confidence", 0.5),
                metadata={"engine": engine_name, "steps": result_dict.get("steps", [])},
            )
            root.add_child(child)

        return root

    def build_from_results(self, query: str, results: List[ReasoningResult]) -> RLTNode:
        """Constrói a árvore diretamente de uma lista de ``ReasoningResult``
        (sem passar por ``ensemble()``) — útil quando o chamador já rodou
        os motores manualmente."""
        root = RLTNode(
            inference_type=PeirceType.DR,
            premise=query,
            conclusion=results[0].conclusion if results else "",
            confidence=results[0].confidence if results else 0.5,
            metadata={"root": True},
        )
        for result in results:
            if not result.available:
                continue
            peirce_type = self.mapper.classify(result)
            root.add_child(RLTNode(
                inference_type=peirce_type,
                premise=query,
                conclusion=result.conclusion,
                confidence=result.confidence,
                metadata={"engine": result.engine, "steps": result.steps},
            ))
        return root


class RLTValidator:
    """Verifica coerência lógica de uma RLT (SPEC-057 Secao 4):
    profundidade máxima, fecho (raiz = conclusão final) e rastreabilidade
    premissa-filho/pai."""

    def __init__(self, max_depth: int = RLTBuilder.MAX_DEPTH):
        self.max_depth = max_depth

    def validate(self, root: RLTNode) -> Dict[str, Any]:
        issues: List[str] = []

        depth = root.depth()
        if depth > self.max_depth:
            issues.append(f"Profundidade {depth} excede o máximo permitido ({self.max_depth}).")

        if not root.conclusion.strip():
            issues.append("Fecho ausente: a raiz não tem conclusão final.")

        # Rastreabilidade: quantos filhos tem conclusao sem nenhuma
        # sobreposicao lexical com a premissa do pai (heuristica de
        # overlap, mesmo espirito do detector de goal drift em
        # trust/trust_engine.py). Informativo — nao bloqueia well_formed
        # sozinho, pois e um proxy grosseiro, nao uma prova semantica.
        untraceable = self._count_untraceable(root)
        total_children = self._count_nodes(root) - 1

        return {
            "well_formed": len(issues) == 0,
            "issues": issues,
            "depth": depth,
            "total_nodes": self._count_nodes(root),
            "untraceable_children": untraceable,
            "total_children": total_children,
            "peirce_types_used": sorted({c.inference_type.name for c in self._flatten(root)}),
        }

    def _count_untraceable(self, node: RLTNode) -> int:
        count = 0
        for child in node.children:
            child_words = set(child.conclusion.lower().split())
            parent_words = set(node.premise.lower().split())
            if not (child_words & parent_words):
                count += 1
            count += self._count_untraceable(child)
        return count

    def _count_nodes(self, node: RLTNode) -> int:
        return 1 + sum(self._count_nodes(c) for c in node.children)

    def _flatten(self, node: RLTNode) -> List[RLTNode]:
        flat = [node]
        for c in node.children:
            flat.extend(self._flatten(c))
        return flat


class RLTVisualizer:
    """Exporta a RLT como dict/JSON ou diagrama Mermaid."""

    def to_json_dict(self, root: RLTNode) -> Dict[str, Any]:
        return root.to_dict()

    def to_mermaid(self, root: RLTNode) -> str:
        lines = ["graph TD"]

        def _walk(node: RLTNode) -> None:
            label = f"{node.id}[\"{node.inference_type.name}: {node.conclusion[:40]}\"]"
            lines.append(f"    {label}")
            for child in node.children:
                lines.append(f"    {node.id} --> {child.id}")
                _walk(child)

        _walk(root)
        return "\n".join(lines)


# Fachada de conveniência
class ArcheRLT:
    """Fachada única do ARCHE RLT: constrói, valida e exporta em um passo."""

    def __init__(self):
        self.mapper = ReasoningMapper()
        self.builder = RLTBuilder(self.mapper)
        self.validator = RLTValidator()
        self.visualizer = RLTVisualizer()

    def analyze(self, query: str, ensemble_result: Dict[str, Any]) -> Dict[str, Any]:
        """Pipeline completo: constrói a árvore a partir de um ensemble
        de raciocínio, valida coerência e exporta."""
        tree = self.builder.build_from_ensemble(query, ensemble_result)
        validation = self.validator.validate(tree)
        return {
            "tree": self.visualizer.to_json_dict(tree),
            "mermaid": self.visualizer.to_mermaid(tree),
            "validation": validation,
        }


arche_rlt = ArcheRLT()
