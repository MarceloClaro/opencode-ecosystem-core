# -*- coding: utf-8 -*-
"""
Loop Specification Engine — SPEC-935-R109
==========================================
Formaliza dentro do SDD existente o conceito de "loop specification"
(Macedo, 2026, arXiv:2607.00038): um artefato limitado e reutilizável —
trigger, objetivo, verificação, regra de parada e memória — que um humano
entrega a um harness de agente para que ele persiga um objetivo sozinho,
em vez de prompting passo a passo.

Este módulo NÃO substitui `SpecRegistry`/`Specification` (que especificam
uma ENTREGA verificada uma vez). `LoopSpecification` especifica um
PROCESSO que se repete até um estado terminal nomeado, com detecção de
estagnação e teto de orçamento — o objeto descrito no paper como distinto
tanto de um loop de programação comum quanto do ciclo interno
percebe-age-observa que o harness já executa por padrão.

Escada de verificação (5 níveis, do paper):
  1. Determinístico (assert, exit code, saída dourada)
  2. Regra/constraint sobre o texto (linter, schema, política)
  3. Verdade de campo atrasada (testes, deploy, resposta real)
  4. Modelo como juiz (rubrica) — opinião, não verdade de campo
  5. Checkpoint humano — supervisão, não verificação automatizada

Níveis 1-2 são a "zona autônoma"; 1-3 são a "zona objetiva"; 4-5 são
"fluxo assistido". Política do módulo: nunca fingir que um nível 4 é
nível 1, e todo juiz de nível 4 exige arquitetura maker-checker (quem
produz não pode ser quem aprova).

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from mci.metabus import metabus

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOOPS_DIR = os.path.join(REPO_ROOT, "specs", "loops")

# Estados terminais nomeados canônicos (o paper: "an error or an exhausted
# budget never counts as success"). Loops podem definir um subconjunto,
# mas nunca podem tratar "error"/"exhausted" como sinônimo de "success".
CANONICAL_TERMINAL_STATES = ["success", "no_op", "blocked", "stalled", "exhausted", "error"]

VALID_TRIGGERS = ("manual", "scheduled", "event")
VALID_ARCHITECTURES = ("solo", "maker_checker", "manager")


def is_stagnant(scores: List[float], window: int = 3, threshold: float = 0.02) -> bool:
    """Detector de estagnação genérico (mesmo formato usado por
    ``agentic_science_v2.evolutionary_engine.EvoEngine.is_stagnant``):
    estagnado se a variação (max-min) das últimas `window` pontuações
    ficar abaixo de `threshold`."""
    if len(scores) < window:
        return False
    recent = scores[-window:]
    if len(recent) < 2:
        return False
    return max(recent) - min(recent) < threshold


@dataclass
class LoopSpecification:
    """Especificação formal de um loop (trigger + goal + verificação +
    parada + memória), seguindo a anatomia de Macedo (2026)."""

    name: str
    description: str
    use_when: str

    trigger: str = "manual"
    trigger_justification: str = ""

    goal: str = ""
    goal_verifiable: bool = True

    verification_level: int = 1
    verification_description: str = ""

    architecture: str = "solo"

    terminal_states: List[str] = field(default_factory=lambda: ["success", "blocked", "exhausted", "error"])

    stagnation_window: int = 3
    stagnation_threshold: float = 0.02
    max_iterations: int = 5

    memory_location: str = ""
    guardrails: List[str] = field(default_factory=list)

    def validate(self) -> Dict[str, Any]:
        """Checklist de boa-formação (Secao 7 do paper): um item por
        elemento da anatomia. Retorna achados e `well_formed` geral."""
        issues: List[str] = []

        if not self.trigger_justification.strip():
            issues.append(
                "Sem justificativa de trigger: um loop só se justifica sobre um "
                "prompt agendado quando o resultado de uma rodada muda a próxima "
                "ação ('golden rule' do paper)."
            )
        if self.trigger not in VALID_TRIGGERS:
            issues.append(f"Trigger '{self.trigger}' inválido (use {VALID_TRIGGERS}).")

        if not self.goal.strip():
            issues.append("Objetivo (goal) não definido.")

        if not (1 <= self.verification_level <= 5):
            issues.append("Nível de verificação fora da escada (1-5).")
        if self.verification_level >= 4 and self.architecture == "solo":
            issues.append(
                "Verificador de nível 4+ (juiz/checkpoint) exige arquitetura "
                "maker-checker ou manager — quem produz não pode ser quem aprova "
                "(anti-padrão 'self-approving loop' / reward hacking)."
            )
        if self.verification_level <= 2 and not self.verification_description.strip():
            issues.append("Verificação determinística/regra sem descrição do check real.")

        if "success" not in self.terminal_states:
            issues.append("Estado terminal 'success' ausente.")
        if len(self.terminal_states) < 2:
            issues.append(
                "Apenas um estado terminal nomeado — precisa distinguir sucesso de "
                "pelo menos um modo de parada (blocked/stalled/exhausted/error/no_op)."
            )
        unknown = [s for s in self.terminal_states if s not in CANONICAL_TERMINAL_STATES]
        if unknown:
            issues.append(f"Estados terminais fora do vocabulário canônico: {unknown}.")

        if self.max_iterations <= 0:
            issues.append("Sem teto de orçamento (max_iterations <= 0) — risco de 'unattended runaway'.")
        if self.stagnation_window <= 0 or self.stagnation_threshold <= 0:
            issues.append("Detector de estagnação mal configurado (window/threshold devem ser > 0).")

        if not self.memory_location.strip():
            issues.append("Memória entre execuções não declarada (estado deve persistir fora da conversa).")

        return {
            "well_formed": len(issues) == 0,
            "issues": issues,
            "verification_zone": self._verification_zone(),
        }

    def _verification_zone(self) -> str:
        if self.verification_level <= 2:
            return "autonomous"
        if self.verification_level == 3:
            return "objective"
        return "assisted"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "use_when": self.use_when,
            "trigger": self.trigger,
            "trigger_justification": self.trigger_justification,
            "goal": self.goal,
            "goal_verifiable": self.goal_verifiable,
            "verification_level": self.verification_level,
            "verification_description": self.verification_description,
            "architecture": self.architecture,
            "terminal_states": self.terminal_states,
            "stagnation_window": self.stagnation_window,
            "stagnation_threshold": self.stagnation_threshold,
            "max_iterations": self.max_iterations,
            "memory_location": self.memory_location,
            "guardrails": self.guardrails,
            "validation": self.validate(),
        }

    def to_markdown(self) -> str:
        v = self.validate()
        lines = [
            f"# {self.name} — Loop Specification",
            "",
            f"**Descrição:** {self.description}",
            "",
            f"**Use quando:** {self.use_when}",
            "",
            "## Trigger",
            f"- Tipo: `{self.trigger}`",
            f"- Justificativa: {self.trigger_justification}",
            "",
            "## Objetivo e Verificação",
            f"- Objetivo: {self.goal}",
            f"- Verificável: {'sim' if self.goal_verifiable else 'não'}",
            f"- Nível na escada de verificação: **{self.verification_level}** "
            f"(zona: {v['verification_zone']})",
            f"- Check real: {self.verification_description}",
            "",
            "## Arquitetura",
            f"- `{self.architecture}`",
            "",
            "## Estados Terminais Nomeados",
        ]
        lines += [f"- `{s}`" for s in self.terminal_states]
        lines += [
            "",
            "## Regra de Parada",
            f"- Detector de estagnação: janela={self.stagnation_window}, "
            f"limiar={self.stagnation_threshold}",
            f"- Teto de orçamento: {self.max_iterations} iterações",
            "",
            "## Memória",
            f"- {self.memory_location}",
            "",
            "## Guardrails",
        ]
        lines += [f"- {g}" for g in self.guardrails] or ["- (nenhum declarado)"]
        lines += [
            "",
            "## Boa-formação (checklist automático)",
            f"- `well_formed`: {v['well_formed']}",
        ]
        if v["issues"]:
            lines += ["- Pendências:"] + [f"  - {i}" for i in v["issues"]]
        return "\n".join(lines) + "\n"

    def export(self, directory: str = LOOPS_DIR) -> str:
        """Grava o documento em specs/loops/<name>-loop.md e retorna o path."""
        os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, f"{self.name}-loop.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_markdown())
        return path


class LoopSpecRegistry:
    """Registro central de loop specs (paralelo ao SpecRegistry de SDD)."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoopSpecRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.loops: Dict[str, LoopSpecification] = {}
        self._initialized = True

    def register(self, loop_spec: LoopSpecification) -> Dict[str, Any]:
        """Registra um loop e publica sua validação no MetaBus. Um loop
        mal-formado ainda é registrado (para visibilidade), mas o
        resultado da validação fica anexado ao registro."""
        validation = loop_spec.validate()
        self.loops[loop_spec.name] = loop_spec
        metabus.publish_subsystem_event(
            "sdd_loop",
            "loop_spec.registered",
            {
                "name": loop_spec.name,
                "well_formed": validation["well_formed"],
                "verification_zone": validation["verification_zone"],
                "issues": validation["issues"],
            },
            source_agent="loop_spec_registry",
        )
        if not validation["well_formed"]:
            metabus.memory.add_reflection(
                agent_id="loop_spec_registry",
                task_context=f"registro do loop spec '{loop_spec.name}'",
                reflection=f"Loop mal-formado: {'; '.join(validation['issues'])}",
                score=0.2,
            )
        return validation

    def get(self, name: str) -> Optional[LoopSpecification]:
        return self.loops.get(name)

    def list(self) -> List[Dict[str, Any]]:
        return [loop.to_dict() for loop in self.loops.values()]


# Singletons globais
loop_spec_registry = LoopSpecRegistry()
