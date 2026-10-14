# -*- coding: utf-8 -*-
"""
Multi-Reasoning Engines — 11 Motores de Raciocínio (v2.0)
=========================================================
Evolução SPEC-917: 4 originais (corrigidos) + 7 novos motores.

ENTRADA MATEMÁTICA: Z3 e SymPy usam gramáticas controladas por AST.
Texto externo não é encaminhado a parsing dinâmico do SymPy. Somente operações
matemáticas explicitamente permitidas são construídas após validação integral.

Motores:
  1. Z3Engine          — lógico-formal SAT/SMT          (z3-solver opcional)
  2. SymPyEngine       — simbólico-matemático           (sympy opcional)
  3. KanrenEngine      — relacional/lógico              (miniKanren opcional)
  4. CriticalEngine    — crítico-dialético              (stdlib)
  5. BayesianEngine    — probabilístico (Bayes)         (numpy opcional)
  6. CausalEngine      — causal (Pearl / Bradford Hill) (stdlib)
  7. TemporalEngine    — ordenação temporal             (stdlib)
  8. FuzzyReasoning    — lógica difusa                  (scipy opcional)
  9. ChainOfThought    — decomposição multi-passo       (stdlib)
  10. AnalogicalEngine — raciocínio analógico           (stdlib)
  11. Counterfactual   — contrafactual ("e se...")      (stdlib)
  12. QuantumReasoning — experimentos quânticos          (stdlib/Qiskit opcional)
"""

from __future__ import annotations

import ast
import math
import operator
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ── Tipos compartilhados ─────────────────────────────────────────────────

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
            "calibrated": False, "confidence_promoted": False,
        }


# ═══════════════════════════════════════════════════════════════════════════
# 1. Z3Engine — Lógico-Formal (CORRIGIDO: sem execução dinâmica)
# ═══════════════════════════════════════════════════════════════════════════

# Operadores lógicos permitidos no parser Z3 controlado
_Z3_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.Eq: operator.eq,
    ast.Gt: operator.gt,
    ast.Lt: operator.lt,
    ast.GtE: operator.ge,
    ast.LtE: operator.le,
}


def _safe_build_z3_constraint(expr: str, variables: Dict[str, Any]) -> Any:
    """Valida integralmente uma fórmula limitada antes de construir Z3.

    O orçamento de potências reutiliza R818. Esses limites sintáticos não
    garantem um teto de memória ou tempo total para toda fórmula aceita.
    """
    if not isinstance(expr, str) or not expr.strip() or len(expr) > 4096:
        raise ValueError("restrição vazia, inválida ou acima do limite")
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ValueError("sintaxe de restrição inválida") from exc
    if sum(1 for _ in ast.walk(tree)) > 256:
        raise ValueError("número de nós acima do limite")

    def validate(node: ast.AST, depth: int = 0) -> str:
        if depth > 32:
            raise ValueError("profundidade acima do limite")
        if isinstance(node, ast.Constant):
            if type(node.value) is bool:
                return "boolean"
            if type(node.value) not in (int, float):
                raise ValueError("somente constantes numéricas ou booleanas")
            if type(node.value) is int and node.value.bit_length() > 256:
                raise ValueError("inteiro acima do limite")
            if type(node.value) is float and not math.isfinite(node.value):
                raise ValueError("constante não finita")
            return "numeric"
        if isinstance(node, ast.Name):
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", node.id) is None:
                raise ValueError("identificador privado ou inválido")
            return "numeric"
        if isinstance(node, ast.UnaryOp):
            kind = validate(node.operand, depth + 1)
            if isinstance(node.op, ast.Not) and kind == "boolean":
                return "boolean"
            if isinstance(node.op, (ast.UAdd, ast.USub)) and kind == "numeric":
                return "numeric"
            raise ValueError("operador unário ou tipo não suportado")
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
            if validate(node.left, depth + 1) != "numeric" or validate(node.right, depth + 1) != "numeric":
                raise ValueError("aritmética exige operandos numéricos")
            if isinstance(node.op, ast.Pow):
                # Somente validação restrita; nenhum objeto SymPy é criado.
                _safe_math_ast(ast.unparse(node))
            return "numeric"
        if isinstance(node, ast.Compare):
            if len(node.ops) != 1 or not isinstance(node.ops[0], (ast.Eq, ast.NotEq, ast.Gt, ast.Lt, ast.GtE, ast.LtE)):
                raise ValueError("apenas comparações simples permitidas")
            if validate(node.left, depth + 1) != "numeric" or validate(node.comparators[0], depth + 1) != "numeric":
                raise ValueError("comparação exige operandos numéricos")
            return "boolean"
        if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
            for value in node.values:
                if validate(value, depth + 1) != "boolean":
                    raise ValueError("operador lógico exige fórmulas booleanas")
            return "boolean"
        raise ValueError(f"nó AST não suportado: {type(node).__name__}")

    if validate(tree.body) != "boolean":
        raise ValueError("restrição deve ser uma fórmula booleana")
    import z3

    # Constrói dict com objetos z3 para variáveis conhecidas
    env: Dict[str, Any] = {}
    for name in variables:
        env[name] = variables[name]
    arithmetic_domains: List[Any] = []

    def _eval_node(node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            if type(node.value) is bool:
                return z3.BoolVal(node.value)
            if type(node.value) is int:
                return z3.IntVal(node.value)
            return z3.RealVal(str(node.value))
        elif isinstance(node, ast.Name):
            if node.id in env:
                return env[node.id]
            # Variável não declarada → cria Int e adiciona
            var = z3.Int(node.id)
            env[node.id] = var
            variables[node.id] = var
            return var
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -_eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return _eval_node(node.operand)
            if isinstance(node.op, ast.Not):
                return z3.Not(_eval_node(node.operand))
            raise ValueError(f"operador unário não suportado: {type(node.op)}")
        elif isinstance(node, ast.BinOp):
            left = _eval_node(node.left)
            right = _eval_node(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                # A gramática usa divisão real usual, inclusive entre dois
                # inteiros; o / de IntRef faria divisão inteira silenciosa.
                if z3.is_true(z3.simplify(right == 0)):
                    raise ValueError("divisão por zero: denominador comprovadamente nulo")
                arithmetic_domains.append(right != 0)
                real_left = z3.ToReal(left) if z3.is_int(left) else left
                real_right = z3.ToReal(right) if z3.is_int(right) else right
                return real_left / real_right
            elif isinstance(node.op, ast.Pow):
                if z3.is_true(z3.simplify(z3.And(left == 0, right < 0))):
                    raise ValueError("potência indefinida: base zero com expoente negativo")
                arithmetic_domains.append(z3.Or(right >= 0, left != 0))
                # Convenção da fachada matemática (também usada pelo SymPy):
                # a**0 = 1, incluindo 0**0; Z3 totaliza 0**0 arbitrariamente.
                if z3.is_true(z3.simplify(right == 0)):
                    return z3.RealVal(1)
                return z3.If(right == 0, z3.RealVal(1), left ** right)
            raise ValueError(f"operador binário não suportado: {type(node.op)}")
        elif isinstance(node, ast.Compare):
            left = _eval_node(node.left)
            if len(node.ops) != 1:
                raise ValueError("apenas comparações simples")
            right = _eval_node(node.comparators[0])
            op = node.ops[0]
            if isinstance(op, ast.Eq):
                return left == right
            elif isinstance(op, ast.NotEq):
                return left != right
            elif isinstance(op, ast.Gt):
                return left > right
            elif isinstance(op, ast.Lt):
                return left < right
            elif isinstance(op, ast.GtE):
                return left >= right
            elif isinstance(op, ast.LtE):
                return left <= right
            raise ValueError(f"operador de comparação não suportado: {type(op)}")
        elif isinstance(node, ast.BoolOp):
            values = [_eval_node(v) for v in node.values]
            if isinstance(node.op, ast.And):
                return z3.And(*values)
            elif isinstance(node.op, ast.Or):
                return z3.Or(*values)
            raise ValueError(f"operador booleano não suportado: {type(node.op)}")
        raise ValueError(f"nó AST não suportado: {type(node)}")

    formula = _eval_node(tree.body)
    # O domínio vale para a fórmula inteira. Dentro de Not/Or, uma guarda
    # poderia ser negada ou ocultada por outro ramo e admitir operações indefinidas.
    return z3.And(*arithmetic_domains, formula) if arithmetic_domains else formula


class Z3Engine:
    """Motor lógico-formal SAT/SMT (z3-solver) com parser AST seguro.

    CORRIGIDO v2.0: execução dinâmica substituída por parser AST controlado.
    """

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
        invalid_collection = constraints is not None and (
            not isinstance(constraints, (list, tuple))
            or len(constraints) > 64
            or any(not isinstance(c, str) for c in constraints)
            or sum(len(c) for c in constraints) > 16384
        )
        if invalid_collection:
            conclusion = "Operação Z3 recusada: forneça até 64 restrições textuais (16384 caracteres totais)"
            confidence = 0.0
        elif not constraints:
            conclusion = (
                "Sem restrições formais: somente tautologia vazia; "
                "a query não avaliada exige uma fórmula explícita"
            )
            confidence = 0.0
        elif self.available:
            try:
                import z3
                solver = z3.Solver()
                solver.set(timeout=5000, rlimit=100000)
                variables: Dict[str, Any] = {}
                for c in constraints:
                    z3_expr = _safe_build_z3_constraint(c, variables)
                    solver.add(z3_expr)
                    steps.append(f"restrição adicionada (safe AST): {c}")
                verdict = solver.check()
                if str(verdict) == "sat":
                    model = solver.model()
                    assignment = {str(d): str(model[d]) for d in model.decls()}
                    conclusion = f"SATISFATÍVEL — modelo: {assignment}"
                    confidence = 0.95
                elif str(verdict) == "unsat":
                    conclusion = f"Veredicto Z3: {verdict}"
                    confidence = 0.9
                else:
                    conclusion = f"Veredicto Z3 inconclusivo: {verdict}"
                    confidence = 0.0
            except Exception as exc:
                conclusion = f"Operação Z3 recusada: {exc}"
                confidence = 0.0
                steps.append("Problema integral recusado; nenhuma conclusão sobre restrições parciais")
        else:
            # Fallback: análise proposicional por contradição direta
            steps.append("z3-solver ausente — fallback proposicional")
            negations = []
            for c in (constraints or []):
                for c2 in (constraints or []):
                    if c2 != c:
                        if f"!{c2}" in c or f"not {c2}" in c:
                            negations.append((c, c2))
            conclusion = (
                f"Possível contradição detectada entre {len(negations)} pares" if negations
                else "Sem contradições diretas detectadas (análise superficial)"
            )
            confidence = 0.4 if not negations else 0.6
        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               self.available, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 2. SymPyEngine — Simbólico-Matemático (CORRIGIDO: sem execução dinâmica)
# ═══════════════════════════════════════════════════════════════════════════

_MATH_CALL_ARITIES = {
    "sin": (1, 1), "cos": (1, 1), "tan": (1, 1), "sqrt": (1, 1),
    "exp": (1, 1), "log": (1, 2), "Abs": (1, 1),
    "solve": (1, 2), "integrate": (2, 2), "diff": (2, 3),
}
_MATH_CONSTANTS = {"pi", "E", "I"}
_MATH_BINARY_OPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow)


def _math_literal_integer(node: ast.AST) -> Optional[int]:
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _math_literal_integer(node.operand)
        if value is not None:
            return -value if isinstance(node.op, ast.USub) else value
    return None


def _safe_math_ast(text: str) -> Tuple[ast.AST, Optional[ast.AST]]:
    """Valida toda a gramática antes de construir ou calcular qualquer objeto.

    Limites sintáticos reduzem entradas patológicas; não constituem timeout
    dos algoritmos de resolução ou integração do backend.
    """
    if not isinstance(text, str) or not text.strip() or len(text) > 4096:
        raise ValueError("texto matemático vazio, inválido ou acima do limite")
    text = text.strip()
    if re.fullmatch(r"[A-Za-z0-9_+\-*/%().,\s=]+", text) is None:
        raise ValueError("caractere fora da gramática matemática")
    if "=" in text:
        if text.count("=") != 1:
            raise ValueError("apenas igualdade simples lhs = rhs é permitida")
        parts = text.split("=")
    else:
        parts = [text]
    try:
        trees = [ast.parse(part.strip(), mode="eval").body for part in parts]
    except (SyntaxError, ValueError, RecursionError) as exc:
        raise ValueError("sintaxe matemática inválida") from exc
    if sum(sum(1 for _ in ast.walk(tree)) for tree in trees) > 256:
        raise ValueError("número de nós acima do limite")

    def validate(node: ast.AST, depth: int = 0) -> None:
        if depth > 32:
            raise ValueError("profundidade acima do limite")
        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise ValueError("somente constantes numéricas são permitidas")
            if isinstance(node.value, int) and node.value.bit_length() > 256:
                raise ValueError("inteiro acima do limite")
            if isinstance(node.value, float) and not math.isfinite(node.value):
                raise ValueError("constante não finita")
        elif isinstance(node, ast.Name):
            if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", node.id) is None:
                raise ValueError("identificador privado ou inválido")
            if node.id in _MATH_CALL_ARITIES:
                raise ValueError("função matemática exige chamada explícita")
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            validate(node.operand, depth + 1)
        elif isinstance(node, ast.BinOp) and isinstance(node.op, _MATH_BINARY_OPS):
            validate(node.left, depth + 1)
            validate(node.right, depth + 1)
            if isinstance(node.op, ast.Pow):
                if any(isinstance(child, ast.BinOp) and isinstance(child.op, ast.Pow)
                       for side in (node.left, node.right) for child in ast.walk(side)):
                    raise ValueError("potências aninhadas não são permitidas")
                exponent = _math_literal_integer(node.right)
                if exponent is None:
                    symbolic = isinstance(node.right, ast.Name) or (
                        isinstance(node.right, ast.UnaryOp)
                        and isinstance(node.right.operand, ast.Name)
                    )
                    if not symbolic:
                        if any(isinstance(child, (ast.Name, ast.Call)) for child in ast.walk(node.right)):
                            raise ValueError("expoente composto simbólico ou por chamada não permitido")
                        # Só aritmética finita já validada; não chama o backend.
                        exponent = _safe_arithmetic_compute(node.right)
                base_nodes = sum(1 for _ in ast.walk(node.left))
                if base_nodes > 16:
                    raise ValueError("base de potência acima do limite")
                if exponent is not None:
                    if abs(exponent) > 256 or base_nodes * max(1, abs(exponent)) > 512:
                        raise ValueError("expoente acima do limite")
                    base = _math_literal_integer(node.left)
                    if base is not None and base.bit_length() * max(1, abs(exponent)) > 4096:
                        raise ValueError("resultado da potência acima do limite")
                    if not any(isinstance(child, (ast.Name, ast.Call)) for child in ast.walk(node.left)):
                        numeric_base = abs(_safe_arithmetic_compute(node.left))
                        if numeric_base not in (0, 1) and abs(math.log2(numeric_base) * exponent) > 4096:
                            raise ValueError("resultado da potência calculada acima do limite")
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in _MATH_CALL_ARITIES:
                raise ValueError("chamada fora da tabela matemática permitida")
            name = node.func.id
            lower, upper = _MATH_CALL_ARITIES[name]
            if node.keywords or not lower <= len(node.args) <= upper:
                raise ValueError("argumentos não permitidos para função matemática")
            for index, argument in enumerate(node.args):
                if name == "integrate" and index == 1 and isinstance(argument, ast.Tuple):
                    if len(argument.elts) != 3 or not isinstance(argument.elts[0], ast.Name):
                        raise ValueError("limites de integral exigem (variável, inferior, superior)")
                    for element in argument.elts:
                        validate(element, depth + 1)
                else:
                    validate(argument, depth + 1)
            if name in {"diff", "integrate", "solve"} and len(node.args) >= 2:
                variable = node.args[1]
                if not isinstance(variable, ast.Name) and not (
                    name == "integrate" and isinstance(variable, ast.Tuple)
                ):
                    raise ValueError("variável matemática deve ser um símbolo simples")
            if name == "diff" and len(node.args) == 3:
                order = _math_literal_integer(node.args[2])
                if order is None or not 0 <= order <= 32:
                    raise ValueError("ordem de derivação inválida ou acima do limite")
        else:
            raise ValueError(f"nó fora da gramática matemática: {type(node).__name__}")

    for tree in trees:
        validate(tree)
    return trees[0], trees[1] if len(trees) == 2 else None


def _require_defined_math_result(value: Any, sympy: Any) -> None:
    """Recusa resultados indefinidos sem exigir finitude de todo símbolo."""
    if isinstance(value, sympy.Basic):
        if value.has(sympy.nan, sympy.zoo, sympy.oo, -sympy.oo):
            raise ValueError("resultado matemático indefinido ou infinito")
    elif isinstance(value, dict):
        for key, item in value.items():
            _require_defined_math_result(key, sympy)
            _require_defined_math_result(item, sympy)
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            _require_defined_math_result(item, sympy)
    elif type(value) is float and not math.isfinite(value):
        raise ValueError("resultado numérico indefinido ou infinito")


def _build_sympy_math(node: ast.AST, sympy: Any) -> Any:
    """Constrói somente objetos de uma AST já validada, sem reparsar texto."""
    functions = {
        "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
        "sqrt": sympy.sqrt, "exp": sympy.exp, "log": sympy.log,
        "Abs": sympy.Abs, "solve": sympy.solve,
        "integrate": sympy.integrate, "diff": sympy.diff,
    }
    constants = {"pi": sympy.pi, "E": sympy.E, "I": sympy.I}
    operations = {ast.Add: operator.add, ast.Sub: operator.sub,
                  ast.Mult: operator.mul, ast.Div: operator.truediv,
                  ast.Mod: operator.mod, ast.Pow: operator.pow}
    if isinstance(node, ast.Constant):
        result = sympy.Integer(node.value) if type(node.value) is int else sympy.Float(node.value)
    elif isinstance(node, ast.Name):
        result = constants[node.id] if node.id in constants else sympy.Symbol(node.id)
    elif isinstance(node, ast.UnaryOp):
        value = _build_sympy_math(node.operand, sympy)
        result = -value if isinstance(node.op, ast.USub) else value
    elif isinstance(node, ast.BinOp):
        result = operations[type(node.op)](_build_sympy_math(node.left, sympy),
                                          _build_sympy_math(node.right, sympy))
    elif isinstance(node, ast.Tuple):
        result = tuple(_build_sympy_math(element, sympy) for element in node.elts)
    elif isinstance(node, ast.Call):
        arguments = [_build_sympy_math(argument, sympy) for argument in node.args]
        if node.func.id == "diff" and len(arguments) == 3:
            arguments[2] = int(arguments[2])
        result = functions[node.func.id](*arguments)
    else:
        raise ValueError("AST matemática não reconhecida")
    _require_defined_math_result(result, sympy)
    return result


class SymPyEngine:
    """Motor simbólico com AST validada e fallback numérico sem sanitização.

    R818: texto externo não é reparsado pelo backend. Somente operações
    matemáticas permitidas são construídas após validação da árvore inteira.
    """

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
        expr = query if expression is None else expression
        try:
            left_ast, right_ast = _safe_math_ast(expr)
            if expression is None and isinstance(left_ast, ast.Name) and right_ast is None:
                if len(left_ast.id) > 1 and left_ast.id not in _MATH_CONSTANTS:
                    raise ValueError("consulta descritiva exige expression matemática explícita")
            if self.available:
                import sympy
                left = _build_sympy_math(left_ast, sympy)
                if right_ast is not None:
                    right = _build_sympy_math(right_ast, sympy)
                    equation = sympy.Eq(left, right)
                    symbols = sorted(equation.free_symbols, key=str)
                    if symbols:
                        solutions = sympy.solve(equation, symbols[0])
                        _require_defined_math_result(solutions, sympy)
                        conclusion = f"soluções para {symbols[0]}: {solutions}"
                    else:
                        conclusion = f"equação sem símbolos: {equation}"
                    steps.append(f"equação resolvida simbolicamente por AST validada: {expr}")
                else:
                    simplified = left if isinstance(left, (list, dict, tuple)) else sympy.simplify(left)
                    _require_defined_math_result(simplified, sympy)
                    conclusion = f"forma simplificada: {simplified}"
                    steps.append(f"expressão simplificada por AST validada: {expr}")
                confidence = 0.95
            else:
                steps.append("sympy ausente — fallback aritmético por AST validada")
                if right_ast is not None:
                    raise ValueError("equações exigem SymPy")
                result = _safe_arithmetic_compute(left_ast)
                conclusion = f"avaliação numérica: {result}"
                confidence = 0.6
        except Exception as exc:
            conclusion = f"expressão matemática recusada: {exc}"
            confidence = 0.0
            steps.append("entrada ou operação recusada; nenhum resultado matemático concluído")
        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               self.available, round(time.time() - started, 4))


def _safe_arithmetic_compute(node: ast.AST) -> float:
    """Calcula somente uma AST numérica validada, recusando resultados não finitos."""
    operations = {
        ast.Add: operator.add, ast.Sub: operator.sub,
        ast.Mult: operator.mul, ast.Div: operator.truediv,
        ast.Pow: operator.pow, ast.Mod: operator.mod,
    }
    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float) and math.isfinite(node.value):
            return float(node.value)
        raise ValueError("constante não numérica ou não finita")
    if isinstance(node, ast.UnaryOp):
        value = _safe_arithmetic_compute(node.operand)
        if isinstance(node.op, ast.USub):
            return -value
        if isinstance(node.op, ast.UAdd):
            return value
        raise ValueError("operador unário não permitido")
    if isinstance(node, ast.BinOp):
        function = operations.get(type(node.op))
        if function is None:
            raise ValueError("operador numérico não permitido")
        value = function(_safe_arithmetic_compute(node.left), _safe_arithmetic_compute(node.right))
        if not math.isfinite(value):
            raise ValueError("resultado numérico não finito")
        return value
    raise ValueError("fallback aceita somente expressões numéricas")


# ═══════════════════════════════════════════════════════════════════════════
# 3. KanrenEngine — Relacional/Lógico
# ═══════════════════════════════════════════════════════════════════════════

class KanrenEngine:
    """Motor relacional miniKanren com fallback de unificação stdlib.

    v2.0: Suporte extendido com unificação por correspondência.
    """

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
        started = time.time()
        steps: List[str] = []
        facts = facts or []
        if self.available and goal:
            try:
                from kanren import Relation, facts as kfacts, run, var
                rel = Relation()
                # Filtra triplas pela relação do goal
                rel_name = goal[1] or ""
                triples = [(s, o) for s, r, o in facts if r == rel_name]
                if triples:
                    kfacts(rel, *triples)
                x = var()
                if goal[0] is None:
                    results = run(0, x, rel(x, goal[2]))
                else:
                    results = run(0, x, rel(goal[0], x))
                conclusion = f"inferências kanren: {list(results)}"
                confidence = 0.9
                steps.append(f"{len(facts)} fatos carregados, goal={goal}")
            except Exception as exc:
                conclusion = f"erro kanren: {exc}"
                confidence = 0.3
        else:
            # Fallback: unificação por correspondência de padrões (stdlib)
            steps.append("miniKanren ausente ou sem goal — fallback de unificação")
            matches = []
            if goal:
                target_s, target_r, target_o = goal
                for s, r, o in facts:
                    if (target_s is None or s == target_s) and \
                       (target_r is None or r == target_r) and \
                       (target_o is None or o == target_o):
                        matches.append((s, r, o))
            conclusion = (
                f"correspondências diretas: {matches}" if matches
                else "nenhuma correspondência encontrada"
            ) if goal else "forneça facts=[(s,r,o),...] e goal=(s|None, r, o|None)"
            confidence = 0.6 if matches else 0.3
        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               self.available, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 4. CriticalEngine — Crítico-Dialético
# ═══════════════════════════════════════════════════════════════════════════

class CriticalEngine:
    """Motor crítico-dialético (tese-antítese-síntese) — 100% stdlib.

    v2.0: Padrões expandidos + análise por modo de discurso.
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
        ("necessário", "É condição necessária, suficiente ou ambos?"),
        ("impossível", "Há precedentes ou condições que tornariam possível?"),
        ("óbvio", "O que está sendo assumido como óbvio que merece escrutínio?"),
    ]

    DISCOURSE_MODES = {
        "empírico": "A evidência apresentada é observacional ou experimental?",
        "normativo": "Qual o quadro normativo que fundamenta o julgamento?",
        "metafísico": "Há pressupostos ontológicos não declarados?",
        "lógico": "A inferência segue forma dedutiva válida?",
        "estético": "O julgamento estético é sustentado por critérios explícitos?",
    }

    def reason(self, query: str, thesis: Optional[str] = None,
               discourse_mode: Optional[str] = None) -> ReasoningResult:
        started = time.time()
        thesis = thesis or query
        steps = [f"TESE: {thesis}"]

        # Antítese baseada em padrões
        challenges = [q for kw, q in self.CHALLENGE_PATTERNS if kw in thesis.lower()]
        if not challenges:
            challenges = [
                "Quais premissas implícitas sustentam essa afirmação?",
                "Que evidência independente a confirmaria ou refutaria?",
                "Qual seria a posição de um cético qualificado?",
            ]

        # Modo de discurso (se especificado)
        if discourse_mode and discourse_mode in self.DISCOURSE_MODES:
            challenges.append(self.DISCOURSE_MODES[discourse_mode])
            steps.append(f"MODO DE DISCURSO: {discourse_mode}")

        antithesis = " | ".join(challenges)
        steps.append(f"ANTÍTESE: {antithesis}")

        # Síntese
        synthesis = (
            f"A afirmação '{thesis[:120]}' deve ser qualificada: aceitar provisoriamente "
            f"mediante evidência, explicitando premissas e limites de validade. "
            f"Pontos críticos a resolver: {len(challenges)} ({', '.join(challenges[:3])})."
        )
        steps.append(f"SÍNTESE: {synthesis}")
        confidence = 0.7

        return ReasoningResult(self.name, query, synthesis, confidence, steps,
                               True, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 5. BayesianEngine — Probabilístico (NOVO)
# ═══════════════════════════════════════════════════════════════════════════

class BayesianEngine:
    """Raciocínio probabilístico via Teorema de Bayes.

    P(A|B) = P(B|A) * P(A) / P(B)

    Suporta inferência bayesiana simples, Bayes ingênuo e odds ratio.
    numpy opcional; fallback 100% stdlib.
    """

    name = "bayesian"

    def __init__(self):
        self._has_numpy = False
        try:
            import numpy  # noqa: F401
            self._has_numpy = True
        except ImportError:
            pass

    @property
    def available(self):
        return True  # Sempre disponível (stdlib suficiente)

    def reason(self, query: str,
               prior: float = 0.5,
               likelihood: float = 0.5,
               evidence: float = 0.5,
               false_positive_rate: float = 0.05,
               false_negative_rate: float = 0.05,
               ) -> ReasoningResult:
        """Bayesian inference.

        Args:
            query: descrição da consulta
            prior: P(A) — probabilidade a priori da hipótese
            likelihood: P(B|A) — probabilidade do evento dado a hipótese
            evidence: P(B) — probabilidade marginal do evento
            false_positive_rate: P(B|¬A)
            false_negative_rate: P(¬B|A)
        """
        started = time.time()
        steps: List[str] = []

        # Caso 1: Bayes direto com evidência fornecida
        if evidence > 0:
            posterior = (likelihood * prior) / evidence
            steps.append(f"Bayes direto: P(A|B) = P(B|A)×P(A)/P(B) = "
                         f"{likelihood}×{prior}/{evidence} = {posterior:.4f}")
            conclusion = (
                f"P(hipótese | evidência) = {posterior:.4f} "
                f"(prior={prior:.3f}, likelihood={likelihood:.3f})"
            )
            confidence = min(0.9, 0.5 + posterior * 0.5)
        else:
            # Caso 2: Calcular P(B) a partir de taxas de erro
            # P(B) = P(B|A)P(A) + P(B|¬A)P(¬A)
            p_not_a = 1.0 - prior
            evidence_computed = likelihood * prior + false_positive_rate * p_not_a
            if evidence_computed > 0:
                posterior = (likelihood * prior) / evidence_computed
                steps.append(
                    f"Bayes com P(B) computado: P(B|A)×P(A) + P(B|¬A)×P(¬A) = "
                    f"{likelihood}×{prior} + {false_positive_rate}×{p_not_a:.3f} = {evidence_computed:.4f}"
                )
                steps.append(f"Posterior: P(A|B) = {posterior:.4f}")
                conclusion = (
                    f"P(hipótese | evidência) = {posterior:.4f} "
                    f"(considerando taxa de falso positivo={false_positive_rate:.3f})"
                )
            else:
                posterior = prior
                conclusion = f"P(B) ≈ 0 — posterior mantido como prior={prior:.3f}"
            confidence = min(0.85, 0.5 + posterior * 0.4)

        # Odds ratio
        if posterior > 0 and posterior < 1:
            odds = posterior / (1.0 - posterior)
            steps.append(f"Odds ratio: {odds:.3f}")
        else:
            odds = float("inf") if posterior >= 1 else 0.0

        steps.append(f"Posterior={posterior:.4f}, Odds={odds:.3f}")

        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               True, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 6. CausalEngine — Causal (NOVO)
# ═══════════════════════════════════════════════════════════════════════════

class CausalEngine:
    """Raciocínio causal baseado nos Critérios de Bradford Hill + Pearl.

    Distingue correlação de causalidade; avalia força, consistência,
    especificidade, temporalidade, gradiente, plausibilidade,
    coerência, evidência experimental e analogia.
    """

    name = "causal"
    available = True

    BRADFORD_HILL = {
        "força": "A magnitude da associação é grande o bastante?",
        "consistência": "A associação é replicada em diferentes estudos/populações?",
        "especificidade": "A causa leva a um efeito específico (não genérico)?",
        "temporalidade": "A causa precede o efeito no tempo?",
        "gradiente": "Há relação dose-resposta (mais causa → mais efeito)?",
        "plausibilidade": "O mecanismo causal é biologicamente/teoricamente plausível?",
        "coerência": "A interpretação causal conflita com o conhecimento estabelecido?",
        "experimental": "Há evidência experimental (RCT/quase-experimental)?",
        "analogia": "Há analogia com relações causais já estabelecidas?",
    }

    CONFOUNDERS = [
        "fator de confusão não controlado",
        "viés de seleção",
        "viés de informação/mensuração",
        "causalidade reversa",
        "variável instrumental ausente",
    ]

    def reason(self, query: str,
               cause: Optional[str] = None,
               effect: Optional[str] = None,
               hill_criteria: Optional[Dict[str, bool]] = None,
               ) -> ReasoningResult:
        started = time.time()
        steps: List[str] = []
        cause = cause or "causa (não especificada)"
        effect = effect or "efeito (não especificado)"
        hill_criteria = hill_criteria or {}

        steps.append(f"ANÁLISE CAUSAL: {cause} → {effect}")

        # Avalia critérios de Bradford Hill
        criteria_met = 0
        criteria_total = len(self.BRADFORD_HILL)
        for criterion, question in self.BRADFORD_HILL.items():
            if criterion in hill_criteria:
                verdict = hill_criteria[criterion]
                status = "✅" if verdict else "❌"
                if verdict:
                    criteria_met += 1
                steps.append(f"  {status} {criterion}: {question} → {'sim' if verdict else 'não'}")
            else:
                steps.append(f"  ➖ {criterion}: {question} (não avaliado)")

        # Confundidores
        steps.append("POTENCIAIS CONFUNDIDORES:")
        active_confounders = [c for c in self.CONFOUNDERS if c in query.lower()]
        for c in active_confounders:
            steps.append(f"  ⚠️ {c}")

        # Conclusão
        ratio = criteria_met / criteria_total if criteria_total else 0
        if ratio >= 0.67:
            conclusion = (
                f"A relação {cause} → {effect} é provavelmente causal. "
                f"{criteria_met}/{criteria_total} critérios de Bradford Hill satisfeitos."
            )
            confidence = 0.6 + ratio * 0.3
        elif ratio >= 0.33:
            conclusion = (
                f"A relação {cause} → {effect} é possivelmente causal, mas requer mais evidência. "
                f"{criteria_met}/{criteria_total} critérios satisfeitos."
            )
            confidence = 0.3 + ratio * 0.4
        else:
            conclusion = (
                f"A relação {cause} → {effect} não estabelece causalidade. "
                f"Apenas {criteria_met}/{criteria_total} critérios satisfeitos. "
                f"Correlação não implica causalidade."
            )
            confidence = 0.2 + ratio * 0.3

        # Recomendação do Próximo Passo (Pearl's Ladder)
        steps.append(f"Escada da Causalidade (Pearl):")
        steps.append(f"  1. Associação: detectada")
        steps.append(f"  2. Intervenção: requer experimento")
        steps.append(f"  3. Contrafactual: requer modelo estrutural")

        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               True, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 7. TemporalEngine — Ordenação Temporal (NOVO)
# ═══════════════════════════════════════════════════════════════════════════

class TemporalEngine:
    """Raciocínio temporal: ordenação de eventos, precedência, ciclos.

    Detecta sequências causais, intervalos, simultaneidade e ciclos
    temporais em listas de eventos com timestamps.
    """

    name = "temporal"
    available = True

    def reason(self, query: str,
               events: Optional[List[Dict[str, Any]]] = None,
               ) -> ReasoningResult:
        """Analisa eventos temporais.

        Args:
            query: descrição da consulta
            events: lista de dicts com keys "nome", "tempo" (numérico ou string)
        """
        started = time.time()
        steps: List[str] = []
        events = events or []

        if not events:
            return ReasoningResult(
                self.name, query, "forneça events=[{nome, tempo}, ...]",
                0.3, ["sem eventos para análise"], True,
                round(time.time() - started, 4),
            )

        steps.append(f"EVENTOS RECEBIDOS: {len(events)}")

        # Tenta converter tempos para float
        parsed: List[Tuple[float, str]] = []
        for ev in events:
            try:
                t = float(ev.get("tempo", 0))
                parsed.append((t, str(ev.get("nome", "?"))))
            except (ValueError, TypeError):
                steps.append(f"  ⚠️ tempo não numérico para '{ev.get('nome')}' — ignorando")

        if not parsed:
            conclusion = "Nenhum evento com tempo parsável"
            confidence = 0.2
        else:
            # Ordenar por tempo
            parsed.sort(key=lambda x: x[0])
            steps.append("ORDENAÇÃO TEMPORAL:")
            for i, (t, name) in enumerate(parsed):
                steps.append(f"  {i + 1}. [{t}] {name}")

            # Detectar ciclos
            if len(parsed) >= 3:
                # Ciclo: A→B→C→A no tempo
                names_in_order = [name for _, name in parsed]
                if names_in_order[-1] == names_in_order[0] and len(set(names_in_order)) < len(names_in_order):
                    steps.append("⚠️ POSSÍVEL CICLO TEMPORAL DETECTADO: o primeiro evento repete-se no final")
                    cycle = True
                else:
                    cycle = False
            else:
                cycle = False

            # Duração total
            total_duration = parsed[-1][0] - parsed[0][0]
            steps.append(f"DURAÇÃO TOTAL: {total_duration}")

            # Intervalos entre eventos consecutivos
            steps.append("INTERVALOS:")
            for i in range(len(parsed) - 1):
                gap = parsed[i + 1][0] - parsed[i][0]
                steps.append(f"  {parsed[i][1]} → {parsed[i + 1][1]}: {gap}")

            conclusion = (
                f"{len(parsed)} eventos ordenados no tempo. "
                f"Primeiro: '{parsed[0][1]}' ({parsed[0][0]}), "
                f"Último: '{parsed[-1][1]}' ({parsed[-1][0]}). "
                f"Duração total: {total_duration}. "
                + ("⚠️ Ciclo temporal detectado." if cycle else "Sem ciclos.")
            )
            confidence = 0.8 if len(parsed) > 1 else 0.5

        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               True, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 8. FuzzyReasoningEngine — Lógica Difusa (NOVO)
# ═══════════════════════════════════════════════════════════════════════════

class FuzzyReasoningEngine:
    """Raciocínio aproximado com lógica difusa (fuzzy).

    Aceita termos linguísticos como "muito", "pouco", "médio", "alto",
    "baixo" e converte para valores de pertinência [0, 1].
    """

    name = "fuzzy"

    # Termos linguísticos → valor de pertinência
    LINGUISTIC_TERMS: Dict[str, float] = {
        "nenhum": 0.0, "nada": 0.0, "zero": 0.0,
        "quase nenhum": 0.1, "quase nada": 0.1,
        "pouco": 0.2, "pouco": 0.2, "baixo": 0.25, "fraca": 0.25, "fraco": 0.25,
        "médio": 0.5, "media": 0.5, "regular": 0.5,
        "alto": 0.75, "alta": 0.75, "forte": 0.75, "muito": 0.8,
        "bastante": 0.85, "extremamente": 0.9,
        "total": 1.0, "completo": 1.0, "certeza": 1.0, "absoluto": 1.0,
    }

    def __init__(self):
        self._has_scipy = False
        try:
            import scipy  # noqa: F401
            self._has_scipy = True
        except ImportError:
            pass

    @property
    def available(self):
        return True

    def reason(self, query: str,
               propositions: Optional[List[Dict[str, Any]]] = None,
               operator: str = "and",
               ) -> ReasoningResult:
        """Raciocínio fuzzy sobre proposições.

        Args:
            query: descrição
            propositions: lista de dicts [{"texto": ..., "termo": ..., "peso": ...}]
            operator: operador de agregação ("and", "or", "average")
        """
        started = time.time()
        steps: List[str] = []
        propositions = propositions or []

        if not propositions:
            # Extrair termos fuzzy da query
            words = query.lower().split()
            found_terms = {}
            for word in words:
                if word in self.LINGUISTIC_TERMS:
                    found_terms[word] = self.LINGUISTIC_TERMS[word]
            if found_terms:
                membership = sum(found_terms.values()) / len(found_terms)
                terms_str = ", ".join(f"{k}={v}" for k, v in found_terms.items())
                steps.append(f"Termos linguísticos detectados: {terms_str}")
                steps.append(f"Pertinência média: {membership:.3f}")
                conclusion = (
                    f"Valor de pertinência fuzzy: {membership:.3f} "
                    f"(baseado em {len(found_terms)} termos: {list(found_terms.keys())})"
                )
                confidence = 0.5 + membership * 0.4
            else:
                conclusion = "Nenhum termo fuzzy detectado na consulta"
                confidence = 0.3
        else:
            # Avaliar proposições
            memberships = []
            for i, prop in enumerate(propositions):
                term = prop.get("termo", "médio").lower()
                membership = self.LINGUISTIC_TERMS.get(term, 0.5)
                weight = prop.get("peso", 1.0)
                memberships.append(membership * weight)
                steps.append(f"  Proposição {i + 1}: '{prop.get('texto', '')}' → "
                             f"termo '{term}' = {membership} (peso={weight})")

            # Agregação
            if operator == "and":
                result = min(memberships) if memberships else 0.5
                steps.append(f"Agregação (AND fuzzy = min): {result:.3f}")
            elif operator == "or":
                result = max(memberships) if memberships else 0.5
                steps.append(f"Agregação (OR fuzzy = max): {result:.3f}")
            else:  # average
                result = sum(memberships) / len(memberships) if memberships else 0.5
                steps.append(f"Agregação (média): {result:.3f}")

            # Defuzzificação triangular
            defuzzified = result * 100  # escala 0-100
            if defuzzified < 25:
                qual = "baixo"
            elif defuzzified < 50:
                qual = "médio-baixo"
            elif defuzzified < 75:
                qual = "médio-alto"
            else:
                qual = "alto"

            conclusion = (
                f"Valor fuzzy agregado: {result:.3f} (escala 0-1). "
                f"Defuzzificação: {defuzzified:.1f}/100 → {qual}."
            )
            confidence = 0.5 + result * 0.4

        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               True, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 9. ChainOfThoughtEngine — Decomposição Multi-Passo (NOVO)
# ═══════════════════════════════════════════════════════════════════════════

class ChainOfThoughtEngine:
    """Raciocínio por Cadeia de Pensamento (Chain-of-Thought).

    Decompõe consultas complexas em sub-passos encadeados,
    cada passo alimentando o próximo.
    """

    name = "chain_of_thought"
    available = True

    # Padrões de decomposição por tipo de consulta
    DECOMPOSERS = {
        "comparar": [
            "Identificar entidades a comparar",
            "Listar atributos relevantes para cada entidade",
            "Estabelecer critérios de comparação",
            "Avaliar cada entidade segundo os critérios",
            "Sintetizar resultado da comparação",
        ],
        "causa": [
            "Identificar efeito observado",
            "Listar causas potenciais",
            "Avaliar evidência para cada causa",
            "Aplicar Navalha de Occam (causa mais parcimoniosa)",
            "Concluir sobre causalidade",
        ],
        "analisar": [
            "Decompor o problema em partes constituintes",
            "Examinar cada parte individualmente",
            "Identificar relações entre as partes",
            "Sintetizar análise integrada",
        ],
        "resolver": [
            "Identificar o que é dado (premissas)",
            "Identificar o que é pedido (conclusão)",
            "Selecionar estratégia de solução",
            "Executar passos intermediários",
            "Verificar consistência do resultado",
        ],
        "padrão": [
            "Coletar observações/discretos",
            "Identificar regularidades",
            "Formular hipótese de padrão",
            "Testar hipótese contra observações",
            "Generalizar ou refutar",
        ],
    }

    DEFAULT_CHAIN = [
        "Compreender a pergunta",
        "Identificar informações relevantes disponíveis",
        "Aplicar raciocínio passo a passo",
        "Verificar consistência interna",
        "Formular resposta final",
    ]

    def reason(self, query: str,
               mode: str = "auto",
               custom_steps: Optional[List[str]] = None,
               ) -> ReasoningResult:
        started = time.time()
        steps: List[str] = []

        # Selecionar cadeia de decomposição
        if custom_steps:
            chain = custom_steps
        elif mode != "auto":
            chain = self.DECOMPOSERS.get(mode, self.DEFAULT_CHAIN)
        else:
            # Detecção automática do modo
            q = query.lower()
            selected_mode = "padrão"
            for key in ["comparar", "comparação", "diferença", "versus", "vs"]:
                if key in q:
                    selected_mode = "comparar"
                    break
            for key in ["causa", "por que", "motivo", "razão"]:
                if key in q:
                    selected_mode = "causa"
                    break
            for key in ["resolver", "calcular", "quanto", "solução"]:
                if key in q:
                    selected_mode = "resolver"
                    break
            for key in ["analisar", "análise", "examinar"]:
                if key in q:
                    selected_mode = "analisar"
                    break
            for key in ["padrão", "regularidade", "tendência", "padrao"]:
                if key in q:
                    selected_mode = "padrão"
                    break
            chain = self.DECOMPOSERS.get(selected_mode, self.DEFAULT_CHAIN)
            steps.append(f"MODO DETECTADO: {selected_mode}")

        # Executar cadeia
        steps.append("CADEIA DE PENSAMENTO:")
        for i, step in enumerate(chain):
            steps.append(f"  Passo {i + 1}: {step}")

        step_count = len(chain)
        conclusion = (
            f"Consulta decomposta em {step_count} passos de raciocínio. "
            f"Cada passo deve ser executado sequencialmente para chegar à conclusão. "
            f"Modo: {mode if mode != 'auto' else selected_mode}."
        )
        confidence = 0.7

        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               True, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 10. AnalogicalEngine — Raciocínio Analógico (NOVO)
# ═══════════════════════════════════════════════════════════════════════════

class AnalogicalEngine:
    """Raciocínio por analogia: mapeamento estrutura-alvo.

    Identifica correspondências entre fonte (domínio conhecido) e
    alvo (domínio problema) para transferir conhecimento.
    """

    name = "analogical"
    available = True

    def reason(self, query: str,
               source: Optional[str] = None,
               target: Optional[str] = None,
               source_attrs: Optional[List[str]] = None,
               target_attrs: Optional[List[str]] = None,
               ) -> ReasoningResult:
        started = time.time()
        steps: List[str] = []
        source = source or "fonte (não especificada)"
        target = target or "alvo (não especificado)"
        source_attrs = source_attrs or []
        target_attrs = target_attrs or []

        steps.append(f"ANALOGIA: {source} → {target}")

        if not source_attrs or not target_attrs:
            # Analogia superficial baseada em similaridade semântica
            source_words = set(source.lower().split())
            target_words = set(target.lower().split())
            common = source_words & target_words
            overlap = len(common) / max(len(source_words | target_words), 1)
            steps.append(f"Similaridade lexical: {overlap:.2%} ({len(common)} termos em comum)")
            if overlap > 0.3:
                conclusion = (
                    f"Similaridade lexical forte ({overlap:.1%}) entre '{source}' e '{target}'. "
                    f"Termos compartilhados: {common}. Analogia potencialmente produtiva."
                )
                confidence = 0.5 + overlap * 0.4
            else:
                conclusion = (
                    f"Similaridade lexical fraca ({overlap:.1%}) entre '{source}' e '{target}'. "
                    f"Para analogia mais precisa, forneça source_attrs e target_attrs."
                )
                confidence = 0.3 + overlap * 0.3
        else:
            # Analogia estrutural: mapear atributos
            steps.append("ATRIBUTOS DA FONTE:")
            for a in source_attrs:
                steps.append(f"  • {a}")
            steps.append("ATRIBUTOS DO ALVO:")
            for a in target_attrs:
                steps.append(f"  • {a}")

            # Correspondência
            matches = []
            for sa in source_attrs:
                for ta in target_attrs:
                    sa_words = set(sa.lower().split())
                    ta_words = set(ta.lower().split())
                    common = sa_words & ta_words
                    if common:
                        matches.append((sa, ta, common))

            if matches:
                steps.append(f"CORRESPONDÊNCIAS ESTRUTURAIS: {len(matches)}")
                for s, t, c in matches:
                    steps.append(f"  {s} ↔ {t} (compartilham: {c})")
                conclusion = (
                    f"Analogia estrutural: {len(matches)} correspondências entre "
                    f"'{source}' e '{target}'. Transferência de conhecimento viável."
                )
                confidence = 0.5 + min(0.4, len(matches) * 0.1)
            else:
                conclusion = (
                    f"Nenhuma correspondência estrutural direta encontrada entre "
                    f"'{source}' e '{target}'. A analogia pode ser distante ou inválida."
                )
                confidence = 0.3

        steps.append(f"Fonte: {source}")
        steps.append(f"Alvo: {target}")

        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               True, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 11. CounterfactualEngine — Raciocínio Contrafactual (NOVO)
# ═══════════════════════════════════════════════════════════════════════════

class CounterfactualEngine:
    """Raciocínio contrafactual: análise "e se..." e "se apenas...".

    Constrói mundos alternativos modificando premissas e avaliando
    consequências. 100% stdlib.
    """

    name = "counterfactual"
    available = True

    def reason(self, query: str,
               fact: Optional[str] = None,
               alternative: Optional[str] = None,
               antecedents: Optional[List[str]] = None,
               ) -> ReasoningResult:
        """Raciocínio contrafactual.

        Args:
            query: consulta descritiva
            fact: enunciado do fato real
            alternative: o que se imagina alternativamente
            antecedents: lista de premissas que seriam diferentes
        """
        started = time.time()
        steps: List[str] = []
        fact = fact or "fato real (não especificado)"
        alternative = alternative or "alternativa (não especificada)"
        antecedents = antecedents or []

        steps.append(f"MUNDO REAL: {fact}")
        steps.append(f"MUNDO CONTRAFACTUAL: {alternative}")

        # Antecedentes modificados
        if antecedents:
            steps.append("ANTECEDENTES ALTERADOS:")
            for a in antecedents:
                steps.append(f"  ↳ {a}")
        else:
            # Extrair antecedentes da consulta
            cf_keywords = ["se", "e se", "caso", "se apenas", "se ao menos"]
            found_ant = []
            q_lower = query.lower()
            for kw in cf_keywords:
                if kw in q_lower:
                    idx = q_lower.index(kw) + len(kw)
                    snippet = query[idx:idx + 100].strip().split(".")[0].strip()
                    if snippet:
                        found_ant.append(snippet)
            antecedents = found_ant if found_ant else ["antecedente não explicitado na consulta"]
            steps.append("ANTECEDENTES (extraídos da consulta):")
            for a in antecedents:
                steps.append(f"  ↳ {a}")

        # Tipos de contrafactual (classificação)
        cf_types = []
        if any(kw in query.lower() for kw in ["se apenas", "se ao menos", "quem dera"]):
            cf_types.append("desejo/arrependimento")
        if any(kw in query.lower() for kw in ["impossível", "não pode", "não é possível"]):
            cf_types.append("impossibilidade")
        if any(kw in query.lower() for kw in ["poderia", "talvez", "possivelmente"]):
            cf_types.append("possibilidade alternativa")
        if not cf_types:
            cf_types.append("contrafactual hipotético")

        steps.append(f"TIPO: {', '.join(cf_types)}")

        # Avaliação da distância do mundo real
        n_changes = len(antecedents)
        distance = min(1.0, n_changes * 0.2)  # +0.2 por antecedente alterado
        steps.append(f"Distância do mundo real: {distance:.2f}")

        conclusion = (
            f"Contrafactual: '{alternative}' substituindo '{fact}'. "
            f"{n_changes} antecedentes alterados (distância={distance:.2f}). "
            f"Tipo: {cf_types[0]}. "
            f"Mundo alternativo plausível com {n_changes} mudanças."
        )
        # Quanto mais distante, menor a confiança
        confidence = max(0.3, 0.9 - distance * 0.5)

        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               True, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# 12. QuantumReasoningEngine — Wrapper do módulo quântico (NOVO)
# ═══════════════════════════════════════════════════════════════════════════

class QuantumReasoningEngine:
    """Motor de raciocínio quântico via `reasoning.quantum`.

    Encapsula a suíte reprodutível Bell/GHZ/Superposição para integrar o
    simulador quântico ao roteamento geral de raciocínio.
    """

    name = "quantum"
    available = True

    def reason(self, query: str,
               n_qubits: int = 2,
               shots: int = 256,
               seeds: Optional[List[int]] = None) -> ReasoningResult:
        started = time.time()
        steps: List[str] = []
        from reasoning.quantum import DEFAULT_SEEDS, run_experiment_suite

        seeds = seeds or DEFAULT_SEEDS[:2]
        report = run_experiment_suite(n_qubits=n_qubits, seeds=seeds, shots=shots)

        steps.append(f"Suíte quântica: n_qubits={n_qubits}, shots={shots}, seeds={seeds}")
        for name, payload in report["experiments"].items():
            steps.append(
                f"Experimento {name}: best_seed={payload['best_seed']}, "
                f"worst_seed={payload['worst_seed']}"
            )

        conclusion = (
            f"experimentos quânticos executados: bell, ghz e superposition "
            f"com {n_qubits} qubits, {shots} shots e {len(seeds)} seeds."
        )
        confidence = 0.85

        return ReasoningResult(self.name, query, conclusion, confidence, steps,
                               True, round(time.time() - started, 4))


# ═══════════════════════════════════════════════════════════════════════════
# MultiReasoningEngine — Fachada Integrada (v2.0)
# ═══════════════════════════════════════════════════════════════════════════

class MultiReasoningEngine:
    """Fachada dos 12 motores + modo ensemble + roteamento expandido."""

    def __init__(self):
        self.engines: Dict[str, object] = {
            "z3": Z3Engine(),
            "sympy": SymPyEngine(),
            "kanren": KanrenEngine(),
            "critical": CriticalEngine(),
            "bayesian": BayesianEngine(),
            "causal": CausalEngine(),
            "temporal": TemporalEngine(),
            "fuzzy": FuzzyReasoningEngine(),
            "chain_of_thought": ChainOfThoughtEngine(),
            "analogical": AnalogicalEngine(),
            "counterfactual": CounterfactualEngine(),
            "quantum": QuantumReasoningEngine(),
        }

    @property
    def available_engines(self) -> List[str]:
        return [name for name, eng in self.engines.items()
                if getattr(eng, 'available', True)]

    def reason(self, query: str, engine: str = "auto", **kwargs) -> ReasoningResult:
        requested_engine = engine
        if engine == "auto":
            engine = "sympy" if kwargs.get("expression") is not None else self._route(query)
        eng = self.engines.get(engine)
        if not eng:
            raise ValueError(
                f"motor desconhecido: {engine}. "
                f"Opções: {list(self.engines)}"
            )
        result = eng.reason(query, **kwargs)
        try:
            from mci.metabus import metabus
            metabus.publish_subsystem_event(
                "reasoning",
                "completed",
                {
                    "query": query[:160],
                    "requested_engine": requested_engine,
                    "selected_engine": engine,
                    "confidence": result.confidence,
                },
                source_agent="reasoning_engine",
            )
            # R886: nota do próprio motor é heurística, não feedback externo.
            # O primário registra a conclusão como observação contextual.
        except Exception:
            pass
        return result

    def status(self) -> Dict[str, bool]:
        return {name: getattr(eng, 'available', True)
                for name, eng in self.engines.items()}

    def ensemble(self, query: str, **kwargs) -> Dict[str, Any]:
        """Executa todos os motores aplicáveis e agrega os resultados.

        Retorna query, results (dict motor→dict), best_engine.
        """
        import inspect
        results = {}
        for name, eng in self.engines.items():
            try:
                params = set(inspect.signature(eng.reason).parameters)
                filtered = {k: v for k, v in kwargs.items() if k in params}
                results[name] = eng.reason(query, **filtered).to_dict()
            except Exception as exc:
                results[name] = {"engine": name, "error": str(exc)[:200]}
        valid = [r for r in results.values() if "confidence" in r]
        best = max(valid, key=lambda r: r["confidence"]) if valid else None
        payload = {
            "query": query,
            "results": results,
            "best_engine": best["engine"] if best else None,
        }
        try:
            from mci.metabus import metabus
            metabus.publish_subsystem_event(
                "reasoning",
                "ensemble.completed",
                {"query": query[:160], "best_engine": payload["best_engine"], "engines": list(results.keys())},
                source_agent="reasoning_engine",
            )
        except Exception:
            pass
        return payload

    @staticmethod
    def _route(query: str) -> str:
        """Roteamento expandido para 11 motores."""
        q = query.lower()

        # Lógico-formal
        if any(k in q for k in ["satisfat", "restrição", "constraint", "sat ", "lógica formal",
                                 "smt", "sat/smt", "formal"]):
            return "z3"

        # Simbólico-matemático
        if re.search(r"\b(?:equação|equações|equation|equations|derivada|derivadas|derivative|integral|integrate|differentiate|diff|solve)\b", q):
            return "sympy"
        try:
            math_ast, equation_ast = _safe_math_ast(query)
            if equation_ast is not None or not isinstance(math_ast, ast.Name) or len(math_ast.id) == 1 or math_ast.id in _MATH_CONSTANTS:
                return "sympy"
        except ValueError:
            pass

        # Relacional
        if any(k in q for k in ["relação", "fato", "quem é", "parentesco", "grafo",
                                 "relacionamento"]):
            return "kanren"

        # Probabilístico
        if any(k in q for k in ["probabilidade", "bayes", "chance", "risco", "aleatório",
                                 "percentual", "odds"]):
            return "bayesian"

        # Causal
        if any(k in q for k in ["causa", "por que", "correlação", "causal", "efeito",
                                 "impacto"]):
            return "causal"

        # Temporal
        if any(k in q for k in ["temporal", "ordem", "sequência", "cronologia", "antes",
                                 "depois", "linha do tempo"]):
            return "temporal"

        # Fuzzy
        if any(k in q for k in ["fuzzy", "difuso", "aproximado", "mais ou menos",
                                 "meio termo"]):
            return "fuzzy"

        # Chain-of-Thought
        if any(k in q for k in ["passo a passo", "raciocinar", "decompor", "analisar",
                                 "etapas"]):
            return "chain_of_thought"

        # Analógico
        if any(k in q for k in ["analogia", "análogo", "similar", "comparação",
                                 "metáfora", "como"]):
            return "analogical"

        # Contrafactual
        if any(k in q for k in ["e se", "contrafactual", "se apenas", "se ao menos",
                                 "alternativo", "outro cenário"]):
            return "counterfactual"

        # Quântico
        if any(k in q for k in ["quântico", "quantico", "qubit", "emaranhamento",
                                 "bell", "ghz", "superposição", "superposicao"]):
            return "quantum"

        # Fallback: crítico-dialético (mais genérico)
        return "critical"


# Singleton
multi_reasoning = MultiReasoningEngine()
