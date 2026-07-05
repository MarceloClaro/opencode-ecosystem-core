# -*- coding: utf-8 -*-
"""
Multi-Reasoning Engines — 4 Motores de Raciocínio
=================================================
Porte Python do multi_reasoning_engine.js do OpenCode_Ecosystem original,
com os 4 motores solicitados:

1. Z3Engine      — raciocínio lógico-formal (SAT/SMT) via z3-solver (opcional)
2. SymPyEngine   — raciocínio simbólico-matemático via sympy (opcional)
3. KanrenEngine  — raciocínio relacional/lógico via miniKanren (opcional)
4. CriticalEngine — raciocínio crítico-dialético (tese-antítese-síntese), stdlib

Cada motor declara `available` conforme a biblioteca externa exista; quando
indisponível, um fallback heurístico stdlib garante que o ecossistema sempre
responda (degradação graciosa). O MultiReasoningEngine roteia consultas para
o motor adequado e pode combinar todos (modo "ensemble").
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ReasoningResult:
    engine: str
    query: str
    conclusion: str
    confidence: float = 0.5
    steps: List[str] = field(default_factory=list)
    available: bool = True
    duration_s: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "engine": self.engine, "query": self.query,
            "conclusion": self.conclusion, "confidence": self.confidence,
            "steps": self.steps, "available": self.available,
            "duration_s": self.duration_s,
        }


class Z3Engine:
    """Motor lógico-formal SAT/SMT (z3-solver) com fallback proposicional simples."""

    name = "z3"

    def __init__(self):
        try:
            import z3  # noqa: F401
            self.available = True
        except ImportError:
            self.available = False

    def reason(self, query: str, constraints: Optional[List[str]] = None) -> ReasoningResult:
        started = time.time()
        steps: List[str] = []
        if self.available:
            import z3
            solver = z3.Solver()
            variables: Dict[str, Any] = {}
            for c in constraints or []:
                try:
                    # Restrições no formato "x > 3", "x + y == 10"
                    names = set(re.findall(r"\b[a-zA-Z_]\w*\b", c)) - {"and", "or", "not"}
                    for n in names:
                        variables.setdefault(n, z3.Int(n))
                    solver.add(eval(c, {"__builtins__": {}}, variables))  # noqa: S307
                    steps.append(f"restrição adicionada: {c}")
                except Exception as exc:
                    steps.append(f"restrição ignorada ({c}): {exc}")
            verdict = solver.check()
            if str(verdict) == "sat":
                model = solver.model()
                assignment = {str(d): str(model[d]) for d in model.decls()}
                conclusion = f"SATISFATÍVEL — modelo: {assignment}"
                confidence = 0.95
            else:
                conclusion = f"Veredicto Z3: {verdict}"
                confidence = 0.9
        else:
            # Fallback: análise proposicional por contradição direta
            steps.append("z3-solver ausente — fallback proposicional")
            negations = [c for c in (constraints or [])
                         if any(f"not {c2}" in c or f"!{c2}" in c
                                for c2 in (constraints or []) if c2 != c)]
            conclusion = ("Possível contradição detectada" if negations
                          else "Sem contradições diretas detectadas (análise superficial)")
            confidence = 0.4
        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               self.available, round(time.time() - started, 4))


class SymPyEngine:
    """Motor simbólico-matemático (sympy) com fallback aritmético stdlib."""

    name = "sympy"

    def __init__(self):
        try:
            import sympy  # noqa: F401
            self.available = True
        except ImportError:
            self.available = False

    def reason(self, query: str, expression: Optional[str] = None) -> ReasoningResult:
        started = time.time()
        steps: List[str] = []
        expr = expression or query
        if self.available:
            import sympy
            try:
                if "=" in expr and "==" not in expr:
                    left, right = expr.split("=", 1)
                    eq = sympy.Eq(sympy.sympify(left), sympy.sympify(right))
                    symbols = sorted(eq.free_symbols, key=str)
                    solutions = sympy.solve(eq, symbols[0]) if symbols else []
                    conclusion = f"soluções para {symbols[0] if symbols else '?'}: {solutions}"
                    steps.append(f"equação resolvida simbolicamente: {expr}")
                else:
                    simplified = sympy.simplify(sympy.sympify(expr))
                    conclusion = f"forma simplificada: {simplified}"
                    steps.append(f"expressão simplificada: {expr}")
                confidence = 0.95
            except Exception as exc:
                conclusion = f"não foi possível processar simbolicamente: {exc}"
                confidence = 0.3
        else:
            steps.append("sympy ausente — fallback aritmético")
            try:
                safe = re.sub(r"[^0-9+\-*/(). ]", "", expr)
                conclusion = f"avaliação numérica: {eval(safe, {'__builtins__': {}})}"  # noqa: S307
                confidence = 0.6
            except Exception:
                conclusion = "expressão não numérica — requer sympy"
                confidence = 0.2
        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               self.available, round(time.time() - started, 4))


class KanrenEngine:
    """Motor relacional miniKanren com fallback de unificação stdlib."""

    name = "kanren"

    def __init__(self):
        try:
            import kanren  # noqa: F401
            self.available = True
        except ImportError:
            self.available = False

    def reason(self, query: str,
               facts: Optional[List[tuple]] = None,
               goal: Optional[tuple] = None) -> ReasoningResult:
        """Raciocínio relacional.

        facts: lista de triplas (sujeito, relação, objeto)
        goal: tripla com None nas posições a inferir, ex.: (None, "parent", "bob")
        """
        started = time.time()
        steps: List[str] = []
        facts = facts or []
        if self.available and goal:
            from kanren import Relation, facts as kfacts, run, var
            rel = Relation()
            triples = [(s, o) for s, r, o in facts if r == (goal[1] or "")]
            if triples:
                kfacts(rel, *triples)
            x = var()
            if goal[0] is None:
                results = run(0, x, rel(x, goal[2]))
            else:
                results = run(0, x, rel(goal[0], x))
            conclusion = f"inferências: {list(results)}"
            confidence = 0.9
            steps.append(f"{len(facts)} fatos carregados, goal={goal}")
        else:
            # Fallback: correspondência direta de padrões sobre as triplas
            steps.append("miniKanren ausente ou sem goal — fallback de unificação")
            matches = []
            if goal:
                for s, r, o in facts:
                    if (goal[0] in (None, s)) and (goal[1] in (None, r)) and (goal[2] in (None, o)):
                        matches.append((s, r, o))
            conclusion = f"correspondências diretas: {matches}" if goal else \
                "forneça facts=[(s,r,o),...] e goal=(s|None, r, o|None)"
            confidence = 0.5 if matches else 0.3
        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               self.available, round(time.time() - started, 4))


class CriticalEngine:
    """Motor crítico-dialético (tese-antítese-síntese) — 100% stdlib.

    Porte do dialectical_engine do repositório original: gera antítese
    sistemática para qualquer afirmação e sintetiza posição balanceada.
    """

    name = "critical"
    available = True

    CHALLENGE_PATTERNS = [
        ("sempre", "Existem contraexemplos em que isso não se sustenta?"),
        ("nunca", "Há condições excepcionais que invalidam a negação absoluta?"),
        ("todos", "A generalização cobre casos de fronteira?"),
        ("melhor", "Melhor segundo qual métrica e para qual contexto?"),
        ("deve", "Qual é a justificativa normativa e quem a valida?"),
        ("causa", "Correlação foi distinguida de causalidade?"),
        ("prova", "A evidência é reprodutível e revisada por pares?"),
    ]

    def reason(self, query: str, thesis: Optional[str] = None) -> ReasoningResult:
        started = time.time()
        thesis = thesis or query
        steps = [f"TESE: {thesis}"]
        challenges = [q for kw, q in self.CHALLENGE_PATTERNS if kw in thesis.lower()]
        if not challenges:
            challenges = [
                "Quais premissas implícitas sustentam essa afirmação?",
                "Que evidência independente a confirmaria ou refutaria?",
                "Qual seria a posição de um cético qualificado?",
            ]
        antithesis = " | ".join(challenges)
        steps.append(f"ANTÍTESE: {antithesis}")
        synthesis = (
            f"A afirmação '{thesis[:120]}' deve ser qualificada: aceitar provisoriamente "
            f"mediante evidência, explicitando premissas e limites de validade. "
            f"Pontos críticos a resolver: {len(challenges)}."
        )
        steps.append(f"SÍNTESE: {synthesis}")
        confidence = 0.7
        return ReasoningResult(self.name, query, synthesis, confidence, steps,
                               True, round(time.time() - started, 4))


class MultiReasoningEngine:
    """Fachada dos 4 motores + modo ensemble."""

    def __init__(self):
        self.engines = {
            "z3": Z3Engine(),
            "sympy": SymPyEngine(),
            "kanren": KanrenEngine(),
            "critical": CriticalEngine(),
        }

    def reason(self, query: str, engine: str = "auto", **kwargs) -> ReasoningResult:
        if engine == "auto":
            engine = self._route(query)
        eng = self.engines.get(engine)
        if not eng:
            raise ValueError(f"motor desconhecido: {engine}. Opções: {list(self.engines)}")
        return eng.reason(query, **kwargs)

    def ensemble(self, query: str, **kwargs) -> Dict[str, Any]:
        """Executa todos os motores aplicáveis e agrega os resultados."""
        results = {}
        for name, eng in self.engines.items():
            try:
                # Passa apenas kwargs suportados por cada motor
                import inspect
                params = set(inspect.signature(eng.reason).parameters)
                filtered = {k: v for k, v in kwargs.items() if k in params}
                results[name] = eng.reason(query, **filtered).to_dict()
            except Exception as exc:
                results[name] = {"engine": name, "error": str(exc)}
        valid = [r for r in results.values() if "confidence" in r]
        best = max(valid, key=lambda r: r["confidence"]) if valid else None
        return {"query": query, "results": results,
                "best_engine": best["engine"] if best else None}

    def status(self) -> Dict[str, bool]:
        return {name: eng.available for name, eng in self.engines.items()}

    @staticmethod
    def _route(query: str) -> str:
        q = query.lower()
        if any(k in q for k in ["resolver", "equação", "simplifi", "derivada", "integral", "="]):
            return "sympy"
        if any(k in q for k in ["satisfat", "restrição", "constraint", "sat ", "lógica formal"]):
            return "z3"
        if any(k in q for k in ["relação", "fato", "quem é", "parentesco", "grafo"]):
            return "kanren"
        return "critical"


# Singleton
multi_reasoning = MultiReasoningEngine()
