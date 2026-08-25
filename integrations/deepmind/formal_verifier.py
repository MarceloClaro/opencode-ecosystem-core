# -*- coding: utf-8 -*-
"""
Formal Proof Verifier — SPEC-935-R442
=====================================
Verificador formal simbólico inspirado nos trabalhos de verificação formal do
Google DeepMind (AlphaProof, AlphaGeometry e LeanProofBench).

Utiliza SymPy e Z3 Solver para validação lógica e algébrica determinística,
eliminando alucinações em passos dedutivos e provas científicas.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from itertools import product
from typing import Any, Dict, List, Optional, Tuple

from integrations.deepmind.formal_safety_predicates import solver_result_proves_implication

try:
    import sympy
    from sympy import simplify
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

try:
    import z3
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False


@dataclass
class VerificationStep:
    """Passo individual de dedução ou prova."""
    step_id: int
    statement: str
    justification: str = ""
    is_valid: bool = False
    details: str = ""
    sympy_verified: bool = False
    z3_verified: bool = False


@dataclass
class FormalVerificationResult:
    """Resultado consolidado da verificação formal."""
    claim: str
    is_valid: bool
    confidence: float
    verified_steps: List[VerificationStep] = field(default_factory=list)
    counterexamples: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    algebraic_equivalent: bool = False
    logic_satisfiable: bool = True
    latex_proof: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "is_valid": self.is_valid,
            "confidence": round(self.confidence, 4),
            "verified_steps": [
                {
                    "step_id": s.step_id,
                    "statement": s.statement,
                    "justification": s.justification,
                    "is_valid": s.is_valid,
                    "details": s.details,
                    "sympy_verified": s.sympy_verified,
                    "z3_verified": s.z3_verified,
                }
                for s in self.verified_steps
            ],
            "counterexamples": self.counterexamples,
            "errors": self.errors,
            "algebraic_equivalent": self.algebraic_equivalent,
            "logic_satisfiable": self.logic_satisfiable,
            "latex_proof": self.latex_proof,
        }


class _RestrictedAlgebraicSyntaxError(ValueError):
    """Indica texto fora da gramática algébrica segura do verificador."""


class FormalProofVerifier:
    """Motor de verificação simbólica e formal de afirmações científicas."""

    _MAX_ALGEBRAIC_EXPRESSION_LENGTH = 1024
    _MAX_ALGEBRAIC_AST_NODES = 128
    _MAX_ALGEBRAIC_AST_DEPTH = 32
    _MAX_IDENTIFIER_LENGTH = 64
    _MAX_INTEGER_BITS = 256
    _MAX_ABSOLUTE_EXPONENT = 256
    _MAX_POWER_NESTING = 1
    _MAX_POWER_BASE_NODES = 16
    _MAX_POWER_EXPANSION_BUDGET = 256
    _MAX_POWER_LITERAL_RESULT_BITS = 4096
    _MAX_COUNTEREXAMPLE_VARIABLES = 8
    _MAX_COUNTEREXAMPLE_TEST_VALUES = 1024
    _MAX_COUNTEREXAMPLE_ASSIGNMENTS = 1024
    _MAX_COUNTEREXAMPLE_VALUE_BITS = 256
    _MAX_PROPOSITIONAL_FORMULA_LENGTH = 1024
    _MAX_PROPOSITIONAL_TOKENS = 256
    _MAX_PROPOSITIONAL_NESTING = 32
    _MAX_PROPOSITIONAL_NEGATIONS = 64
    _MAX_PROPOSITIONAL_NEGATION_CHAIN = 32
    _MAX_PROPOSITIONAL_IMPLICATIONS = 32
    _MAX_LOGICAL_PREMISES = 64
    _MAX_LOGICAL_AGGREGATE_TEXT_LENGTH = 8192
    _MAX_LOGICAL_ATOMS = 64
    _Z3_SOLVER_TIMEOUT_MS = 1000
    _MAX_PROOF_STEPS = 64
    _MAX_PROOF_AGGREGATE_TEXT_LENGTH = 16384
    _IDENTIFIER_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
    _ALLOWED_FUNCTIONS = frozenset({"sin", "cos"})
    _PROPOSITIONAL_SYNTAX_TOKENS = frozenset(
        {"AND", "OR", "NOT", "IMPLIES", "IFF", "TRUE", "FALSE", "(", ")"}
    )

    def __init__(self) -> None:
        self.has_sympy = SYMPY_AVAILABLE
        self.has_z3 = Z3_AVAILABLE

    @staticmethod
    def _has_valid_algebraic_operands(lhs_str: Any, rhs_str: Any) -> bool:
        """Confirma os invariantes mínimos de uma igualdade algébrica.

        Esta validação precisa ocorrer antes de qualquer fallback: dois
        operandos vazios não constituem uma identidade, ainda que sua forma
        textual normalizada coincida.
        """
        return (
            type(lhs_str) is str
            and type(rhs_str) is str
            and bool(lhs_str.strip())
            and bool(rhs_str.strip())
            and "=" not in lhs_str
            and "=" not in rhs_str
        )

    @classmethod
    def _validate_identifier(cls, identifier: Any) -> None:
        """Aceita apenas identificadores simples, sem nomes mágicos."""
        if (
            type(identifier) is not str
            or len(identifier) > cls._MAX_IDENTIFIER_LENGTH
            or cls._IDENTIFIER_PATTERN.fullmatch(identifier) is None
            or identifier.startswith("_")
        ):
            raise _RestrictedAlgebraicSyntaxError("identificador algébrico não permitido")

    @classmethod
    def _literal_integer_value(cls, node: ast.AST) -> Optional[int]:
        """Obtém um expoente inteiro literal, sem avaliar uma expressão textual."""
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if (
            isinstance(node, ast.UnaryOp)
            and isinstance(node.op, (ast.UAdd, ast.USub))
            and isinstance(node.operand, ast.Constant)
            and type(node.operand.value) is int
        ):
            value = node.operand.value
            return value if isinstance(node.op, ast.UAdd) else -value
        return None

    @staticmethod
    def _validate_raw_algebraic_text(expression: str) -> None:
        """Recusa texto algébrico ambíguo antes de delegá-lo ao parser Python.

        O Python normaliza alguns identificadores Unicode durante a análise da
        AST e também aceita comentários em modo ``eval``. Nenhum desses
        comportamentos pertence à linguagem formal restrita deste verificador;
        por isso, a guarda deve preceder incondicionalmente ``ast.parse``.
        """
        if not expression.isascii():
            raise _RestrictedAlgebraicSyntaxError(
                "texto algébrico deve conter apenas caracteres ASCII"
            )
        if "#" in expression:
            raise _RestrictedAlgebraicSyntaxError(
                "comentários não são permitidos em expressões algébricas"
            )

    @classmethod
    def _parse_restricted_algebraic_ast(
        cls,
        expression: Any,
        *,
        allow_relational: bool = False,
    ) -> ast.AST:
        """Analisa a gramática formal permitida sem executar texto fornecido.

        São aceitos literais inteiros exatos, símbolos simples, ``+``, ``-``,
        ``*``, ``/``, potência inteira limitada e chamadas unárias a ``sin`` e
        ``cos``. Racionais devem ser expressos como divisões de inteiros;
        ``float`` e ``complex`` textuais não pertencem ao fragmento. Para a
        busca de contraexemplos, uma comparação binária entre duas expressões
        dessa gramática também é aceita. Todo outro nó da AST é recusado antes
        da construção de qualquer objeto SymPy.
        """
        if type(expression) is not str or not expression.strip():
            raise _RestrictedAlgebraicSyntaxError("expressão algébrica vazia ou não textual")
        if len(expression) > cls._MAX_ALGEBRAIC_EXPRESSION_LENGTH:
            raise _RestrictedAlgebraicSyntaxError("expressão algébrica excede o limite de tamanho")
        cls._validate_raw_algebraic_text(expression)

        try:
            parsed = ast.parse(expression.strip(), mode="eval")
        except (MemoryError, OverflowError, RecursionError, SyntaxError, ValueError) as exc:
            raise _RestrictedAlgebraicSyntaxError("sintaxe algébrica não permitida") from exc

        node_count = 0
        power_budget = 0

        def count_node(node: ast.AST, depth: int) -> None:
            nonlocal node_count
            node_count += 1
            if node_count > cls._MAX_ALGEBRAIC_AST_NODES:
                raise _RestrictedAlgebraicSyntaxError("expressão algébrica excede o limite de nós")
            if depth > cls._MAX_ALGEBRAIC_AST_DEPTH:
                raise _RestrictedAlgebraicSyntaxError("expressão algébrica excede o limite de profundidade")

        def validate_numeric_literal(value: Any) -> None:
            # A AST do Python já materializa ``float`` e ``complex`` antes de
            # SymPy. Aceitá-los permitiria que arredondamentos textuais fossem
            # confundidos com igualdades formais exatas.
            if type(value) is not int:
                raise _RestrictedAlgebraicSyntaxError(
                    "somente literais inteiros exatos são permitidos; "
                    "racionais devem usar divisão de inteiros"
                )
            if value.bit_length() > cls._MAX_INTEGER_BITS:
                raise _RestrictedAlgebraicSyntaxError("literal inteiro excede o limite permitido")

        def validate_algebraic(node: ast.AST, depth: int, power_nesting: int = 0) -> int:
            nonlocal power_budget
            count_node(node, depth)
            if isinstance(node, ast.Name):
                cls._validate_identifier(node.id)
                return 1
            if isinstance(node, ast.Constant):
                validate_numeric_literal(node.value)
                return 1
            if isinstance(node, ast.UnaryOp):
                if not isinstance(node.op, (ast.UAdd, ast.USub)):
                    raise _RestrictedAlgebraicSyntaxError("operador unário não permitido")
                return 1 + validate_algebraic(node.operand, depth + 1, power_nesting)
            if isinstance(node, ast.BinOp):
                if not isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
                    raise _RestrictedAlgebraicSyntaxError("operador algébrico não permitido")
                if isinstance(node.op, ast.Pow):
                    exponent = cls._literal_integer_value(node.right)
                    if exponent is None or abs(exponent) > cls._MAX_ABSOLUTE_EXPONENT:
                        raise _RestrictedAlgebraicSyntaxError(
                            "expoente deve ser um inteiro literal dentro do limite permitido"
                        )
                    literal_base = cls._literal_integer_value(node.left)
                    if exponent <= 0 and (literal_base is None or literal_base == 0):
                        raise _RestrictedAlgebraicSyntaxError(
                            "expoente não positivo exige base literal inteira não nula"
                        )
                    if power_nesting >= cls._MAX_POWER_NESTING:
                        raise _RestrictedAlgebraicSyntaxError(
                            "potências aninhadas não pertencem ao fragmento formal"
                        )

                    # A validação recursiva ainda ocorre inteiramente sobre a
                    # AST; nenhum objeto SymPy é construído antes dos limites
                    # de composição, crescimento e orçamento acumulado.
                    base_nodes = validate_algebraic(node.left, depth + 1, power_nesting + 1)
                    exponent_nodes = validate_algebraic(
                        node.right,
                        depth + 1,
                        power_nesting + 1,
                    )
                    if base_nodes > cls._MAX_POWER_BASE_NODES:
                        raise _RestrictedAlgebraicSyntaxError(
                            "base de potência excede o limite estrutural permitido"
                        )

                    power_cost = max(1, abs(exponent)) * max(1, base_nodes)
                    if power_budget + power_cost > cls._MAX_POWER_EXPANSION_BUDGET:
                        raise _RestrictedAlgebraicSyntaxError(
                            "expressão excede o orçamento acumulado de potências"
                        )

                    if literal_base is not None:
                        result_bits = max(1, abs(literal_base).bit_length()) * abs(exponent)
                        if result_bits > cls._MAX_POWER_LITERAL_RESULT_BITS:
                            raise _RestrictedAlgebraicSyntaxError(
                                "potência literal excede o limite de crescimento exato"
                            )

                    power_budget += power_cost
                    return 1 + base_nodes + exponent_nodes

                if isinstance(node.op, ast.Div):
                    denominator = cls._literal_integer_value(node.right)
                    if denominator is None or denominator == 0:
                        raise _RestrictedAlgebraicSyntaxError(
                            "divisão exige denominador literal inteiro não nulo"
                        )

                left_nodes = validate_algebraic(node.left, depth + 1, power_nesting)
                right_nodes = validate_algebraic(node.right, depth + 1, power_nesting)
                return 1 + left_nodes + right_nodes
            if isinstance(node, ast.Call):
                if (
                    not isinstance(node.func, ast.Name)
                    or node.func.id not in cls._ALLOWED_FUNCTIONS
                    or node.keywords
                    or len(node.args) != 1
                ):
                    raise _RestrictedAlgebraicSyntaxError("chamada de função não permitida")
                return 1 + validate_algebraic(node.args[0], depth + 1, power_nesting)
            raise _RestrictedAlgebraicSyntaxError("construção sintática algébrica não permitida")

        root = parsed.body
        if allow_relational and isinstance(root, ast.Compare):
            count_node(root, 1)
            if len(root.ops) != 1 or len(root.comparators) != 1 or not isinstance(
                root.ops[0], (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE)
            ):
                raise _RestrictedAlgebraicSyntaxError("comparação algébrica não permitida")
            validate_algebraic(root.left, 2)
            validate_algebraic(root.comparators[0], 2)
        else:
            validate_algebraic(root, 1)
        return root

    @staticmethod
    def _algebraic_free_symbol_names(node: ast.AST) -> set[str]:
        """Extrai símbolos livres de uma AST algébrica já validada.

        Nomes de funções permitidas não são variáveis livres. A extração ocorre
        sobre a AST restrita, antes da construção da expressão SymPy, para que
        uma busca de contraexemplos nunca deixe um símbolo sem substituição.
        """
        function_name_nodes = {
            id(current.func)
            for current in ast.walk(node)
            if isinstance(current, ast.Call) and isinstance(current.func, ast.Name)
        }
        return {
            current.id
            for current in ast.walk(node)
            if isinstance(current, ast.Name) and id(current) not in function_name_nodes
        }

    @classmethod
    def _build_sympy_expression(cls, node: ast.AST) -> Any:
        """Constrói objetos SymPy somente a partir de uma AST já validada."""
        if isinstance(node, ast.Name):
            return sympy.Symbol(node.id)
        if isinstance(node, ast.Constant):
            if type(node.value) is int:
                return sympy.Integer(node.value)
        if isinstance(node, ast.UnaryOp):
            operand = cls._build_sympy_expression(node.operand)
            if isinstance(node.op, ast.UAdd):
                return operand
            if isinstance(node.op, ast.USub):
                return sympy.Mul(sympy.Integer(-1), operand)
        if isinstance(node, ast.BinOp):
            left = cls._build_sympy_expression(node.left)
            right = cls._build_sympy_expression(node.right)
            if isinstance(node.op, ast.Add):
                return sympy.Add(left, right)
            if isinstance(node.op, ast.Sub):
                return sympy.Add(left, sympy.Mul(sympy.Integer(-1), right))
            if isinstance(node.op, ast.Mult):
                return sympy.Mul(left, right)
            if isinstance(node.op, ast.Div):
                return sympy.Mul(left, sympy.Pow(right, sympy.Integer(-1)))
            if isinstance(node.op, ast.Pow):
                return sympy.Pow(left, right)
        if isinstance(node, ast.Call):
            argument = cls._build_sympy_expression(node.args[0])
            if node.func.id == "sin":
                return sympy.sin(argument)
            if node.func.id == "cos":
                return sympy.cos(argument)
        if isinstance(node, ast.Compare):
            left = cls._build_sympy_expression(node.left)
            right = cls._build_sympy_expression(node.comparators[0])
            relation_builders = {
                ast.Eq: sympy.Eq,
                ast.NotEq: sympy.Ne,
                ast.Lt: sympy.Lt,
                ast.LtE: sympy.Le,
                ast.Gt: sympy.Gt,
                ast.GtE: sympy.Ge,
            }
            for operator_type, builder in relation_builders.items():
                if isinstance(node.ops[0], operator_type):
                    return builder(left, right)
        raise _RestrictedAlgebraicSyntaxError("AST algébrica não validada")

    @classmethod
    def _is_well_formed_fallback_algebraic_expression(cls, expression: str) -> bool:
        """Valida a mesma gramática restrita usada quando SymPy está disponível."""
        try:
            cls._parse_restricted_algebraic_ast(expression)
        except _RestrictedAlgebraicSyntaxError:
            return False
        return True

    @classmethod
    def _validate_counterexample_variables(cls, var_names: Any) -> List[str]:
        """Valida os nomes e o volume de substituições numéricas solicitadas."""
        if type(var_names) is not list or len(var_names) > cls._MAX_COUNTEREXAMPLE_VARIABLES:
            raise _RestrictedAlgebraicSyntaxError("lista de variáveis não permitida")
        validated_names: List[str] = []
        for name in var_names:
            cls._validate_identifier(name)
            validated_names.append(name)
        if len(set(validated_names)) != len(validated_names):
            raise _RestrictedAlgebraicSyntaxError("nomes de variáveis devem ser distintos")
        return validated_names

    @staticmethod
    def _split_algebraic_equation(statement: Any) -> Optional[Tuple[str, str]]:
        """Separa uma igualdade algébrica bem formada ou a recusa.

        Apenas ``=`` e ``==`` isolados são aceitos. Operadores relacionais e
        lógicos que contêm ``=`` (por exemplo, ``!=`` e ``=>``), múltiplas
        igualdades e operandos vazios são tratados como entrada malformada.
        """
        if type(statement) is not str:
            return None

        normalized = statement.strip()
        if not normalized:
            return None

        equality_start = -1
        equality_width = 0
        position = 0
        while position < len(normalized):
            if normalized[position] != "=":
                position += 1
                continue

            current_width = (
                2
                if position + 1 < len(normalized) and normalized[position + 1] == "="
                else 1
            )
            if equality_start >= 0:
                return None
            equality_start = position
            equality_width = current_width
            position += current_width

        if equality_start < 0:
            return None

        lhs = normalized[:equality_start].strip()
        rhs = normalized[equality_start + equality_width:].strip()
        if not FormalProofVerifier._has_valid_algebraic_operands(lhs, rhs):
            return None

        # Não confundir uma igualdade com comparadores ou setas lógicas.
        if lhs.endswith(("<", ">", "!", ":")) or rhs.startswith(("<", ">", "!")):
            return None

        return lhs, rhs

    @staticmethod
    def _canonical_algebraic_ast(node: ast.AST) -> str:
        """Produz uma representação estrutural, sem posições ou espaços fonte."""
        return ast.dump(node, annotate_fields=True, include_attributes=False)

    @classmethod
    def _parse_restricted_algebraic_equation(
        cls,
        statement: Any,
    ) -> Tuple[str, str, Tuple[str, str]]:
        """Valida uma igualdade e retorna seus operandos e chave AST canônica."""
        if type(statement) is not str:
            raise _RestrictedAlgebraicSyntaxError("igualdade algébrica não textual")
        cls._validate_raw_algebraic_text(statement)

        equation = cls._split_algebraic_equation(statement)
        if equation is None:
            raise _RestrictedAlgebraicSyntaxError(
                "igualdade algébrica malformada ou com operador não permitido"
            )

        lhs, rhs = equation
        lhs_ast = cls._parse_restricted_algebraic_ast(lhs)
        rhs_ast = cls._parse_restricted_algebraic_ast(rhs)
        return (
            lhs,
            rhs,
            (
                cls._canonical_algebraic_ast(lhs_ast),
                cls._canonical_algebraic_ast(rhs_ast),
            ),
        )

    def verify_algebraic_identity(self, lhs_str: str, rhs_str: str) -> Tuple[bool, str]:
        """Verifica se lhs == rhs simbolicamente via SymPy."""
        if not self._has_valid_algebraic_operands(lhs_str, rhs_str):
            return False, (
                "Expressões algébricas malformadas: ambos os operandos devem ser "
                "não vazios e não podem conter '='"
            )

        try:
            lhs_ast = self._parse_restricted_algebraic_ast(lhs_str)
            rhs_ast = self._parse_restricted_algebraic_ast(rhs_str)
        except _RestrictedAlgebraicSyntaxError as exc:
            return False, f"Expressão algébrica recusada: {exc}"

        if not self.has_sympy:
            # Fallback determinístico restrito a uma identidade reflexiva válida.
            clean_lhs = lhs_str.strip().replace(" ", "")
            clean_rhs = rhs_str.strip().replace(" ", "")
            if clean_lhs == clean_rhs:
                return True, "Identidade sintática exata (SymPy indisponível)"
            return False, "SymPy indisponível para verificação algébrica não-trivial"

        try:
            lhs = self._build_sympy_expression(lhs_ast)
            rhs = self._build_sympy_expression(rhs_ast)
            diff = simplify(lhs - rhs)
            if diff == 0:
                return True, f"Identidade confirmada simbolicamente: {lhs_str} ≡ {rhs_str}"
            return False, f"Diferença não-nula: {diff}"
        except Exception as exc:
            return False, f"Erro ao analisar expressões simbólicas: {str(exc)}"

    @classmethod
    def _tokenize_propositional_formula(cls, formula: str) -> Optional[List[str]]:
        """Tokeniza o pequeno fragmento proposicional aceito pelo verificador.

        O método deliberadamente não tenta interpretar linguagem natural. Uma
        fórmula fora deste fragmento deve ser recusada, em vez de ser tratada
        como uma demonstração por heurística.
        """
        if (
            not isinstance(formula, str)
            or len(formula) > cls._MAX_PROPOSITIONAL_FORMULA_LENGTH
            or not formula.strip()
        ):
            return None

        token_pattern = re.compile(
            r"(?:<=>|<->|=>|->|→|↔|∧|∨|¬|!|~|\(|\)|&|\||"
            r"\b(?:and|or|not|implies|iff|true|false)\b|"
            r"[A-Za-z_][A-Za-z0-9_]*)",
            re.IGNORECASE,
        )
        tokens: List[str] = []
        position = 0
        parenthesis_depth = 0
        negation_count = 0
        negation_chain = 0
        implication_count = 0
        while position < len(formula):
            if formula[position].isspace():
                position += 1
                continue
            match = token_pattern.match(formula, position)
            if match is None:
                return None
            token = match.group(0)
            normalized = token.lower()
            token_map = {
                "and": "AND",
                "∧": "AND",
                "&": "AND",
                "or": "OR",
                "∨": "OR",
                "|": "OR",
                "not": "NOT",
                "¬": "NOT",
                "!": "NOT",
                "~": "NOT",
                "implies": "IMPLIES",
                "->": "IMPLIES",
                "=>": "IMPLIES",
                "→": "IMPLIES",
                "iff": "IFF",
                "<->": "IFF",
                "<=>": "IFF",
                "↔": "IFF",
                "true": "TRUE",
                "false": "FALSE",
            }
            normalized_token = token_map.get(normalized, token)

            # Os limites são aplicados durante a tokenização, antes que os
            # parsers recursivos ou o construtor Z3 recebam a fórmula.
            if len(tokens) >= cls._MAX_PROPOSITIONAL_TOKENS:
                return None
            if normalized_token == "(":
                parenthesis_depth += 1
                if parenthesis_depth > cls._MAX_PROPOSITIONAL_NESTING:
                    return None
            elif normalized_token == ")":
                parenthesis_depth -= 1
                if parenthesis_depth < 0:
                    return None

            if normalized_token == "NOT":
                negation_count += 1
                negation_chain += 1
                if (
                    negation_count > cls._MAX_PROPOSITIONAL_NEGATIONS
                    or negation_chain > cls._MAX_PROPOSITIONAL_NEGATION_CHAIN
                ):
                    return None
            else:
                negation_chain = 0

            # A implicação é associativa à direita e, portanto, consome a
            # pilha do parser mesmo sem parênteses explícitos.
            if normalized_token == "IMPLIES":
                implication_count += 1
                if implication_count > cls._MAX_PROPOSITIONAL_IMPLICATIONS:
                    return None

            tokens.append(normalized_token)
            position = match.end()
        if parenthesis_depth != 0:
            return None
        return tokens

    @staticmethod
    def _is_well_formed_propositional_formula(formula: Any) -> bool:
        """Valida a sintaxe proposicional antes de usar qualquer fallback."""
        tokens = FormalProofVerifier._tokenize_propositional_formula(formula)
        if not tokens:
            return False

        position = 0

        def peek() -> Optional[str]:
            return tokens[position] if position < len(tokens) else None

        def consume(expected: Optional[str] = None) -> bool:
            nonlocal position
            token = peek()
            if token is None or (expected is not None and token != expected):
                return False
            position += 1
            return True

        def parse_primary() -> bool:
            token = peek()
            if token == "(":
                return consume("(") and parse_iff() and consume(")")
            if token in {"TRUE", "FALSE"}:
                return consume()
            if token is None or token in {"AND", "OR", "NOT", "IMPLIES", "IFF", ")"}:
                return False
            return consume()

        def parse_unary() -> bool:
            if peek() == "NOT":
                return consume("NOT") and parse_unary()
            return parse_primary()

        def parse_conjunction() -> bool:
            if not parse_unary():
                return False
            while peek() == "AND":
                if not consume("AND") or not parse_unary():
                    return False
            return True

        def parse_disjunction() -> bool:
            if not parse_conjunction():
                return False
            while peek() == "OR":
                if not consume("OR") or not parse_conjunction():
                    return False
            return True

        def parse_implication() -> bool:
            if not parse_disjunction():
                return False
            if peek() == "IMPLIES":
                return consume("IMPLIES") and parse_implication()
            return True

        def parse_iff() -> bool:
            if not parse_implication():
                return False
            while peek() == "IFF":
                if not consume("IFF") or not parse_implication():
                    return False
            return True

        try:
            return parse_iff() and position == len(tokens)
        except RecursionError:
            return False

    @classmethod
    def _snapshot_logical_input(
        cls,
        premises: Any,
        conclusion: Any,
    ) -> Tuple[Optional[Tuple[Tuple[str, ...], str]], Optional[str]]:
        """Valida e congela a única visão consumível de uma implicação lógica.

        A lista e as fórmulas precisam ser objetos nativos exatos. Após a
        validação de volume e tamanho agregado, as premissas são mantidas em
        uma tupla e a conclusão, que já é uma ``str`` nativa imutável, é
        vinculada ao snapshot. As fases posteriores não podem reler a lista do
        chamador.
        """
        if type(premises) is not list:
            return None, "Premissas devem ser fornecidas em uma lista finita estrita"

        premise_count = len(premises)
        if premise_count > cls._MAX_LOGICAL_PREMISES:
            return None, "Quantidade de premissas excede o limite global permitido"
        if type(conclusion) is not str:
            return None, "Premissas e conclusão devem ser fórmulas textuais"

        snapshot_premises: List[str] = []
        for premise_index in range(premise_count):
            try:
                premise = premises[premise_index]
            except IndexError:
                return None, "A lista de premissas foi alterada durante a validação"
            if type(premise) is not str:
                return None, "Premissas e conclusão devem ser fórmulas textuais"
            snapshot_premises.append(premise)

        aggregate_length = len(conclusion)
        for premise in snapshot_premises:
            aggregate_length += len(premise)
            if aggregate_length > cls._MAX_LOGICAL_AGGREGATE_TEXT_LENGTH:
                return None, "Tamanho agregado das fórmulas excede o limite global permitido"

        return (tuple(snapshot_premises), conclusion), None

    @classmethod
    def _logical_input_budget_error(cls, premises: Any, conclusion: Any) -> Optional[str]:
        """Mantém a consulta de orçamento compatível com o snapshot estrito."""
        _, error = cls._snapshot_logical_input(premises, conclusion)
        return error

    @classmethod
    def _propositional_atom_names(cls, tokens: List[str]) -> set[str]:
        """Extrai os átomos de tokens proposicionais já limitados."""
        return {
            token
            for token in tokens
            if token not in cls._PROPOSITIONAL_SYNTAX_TOKENS
        }

    def _parse_propositional_formula(
        self,
        formula: str,
        context: Dict[str, Any],
    ) -> Optional[Any]:
        """Converte uma fórmula proposicional estrita em uma expressão Z3.

        A gramática é propositalmente pequena: negação, conjunção, disjunção,
        implicação, bicondicional, parênteses e átomos booleanos. A recusa de
        construções desconhecidas mantém a verificação fail-closed.
        """
        if not self.has_z3 or not self._is_well_formed_propositional_formula(formula):
            return None

        tokens = self._tokenize_propositional_formula(formula)
        if not tokens:
            return None

        position = 0

        def peek() -> Optional[str]:
            return tokens[position] if position < len(tokens) else None

        def consume(expected: Optional[str] = None) -> Optional[str]:
            nonlocal position
            token = peek()
            if token is None or (expected is not None and token != expected):
                return None
            position += 1
            return token

        def parse_primary() -> Optional[Any]:
            token = peek()
            if token is None:
                return None
            if token == "(":
                consume("(")
                expression = parse_iff()
                if expression is None or consume(")") is None:
                    return None
                return expression
            if token == "TRUE":
                consume("TRUE")
                return z3.BoolVal(True)
            if token == "FALSE":
                consume("FALSE")
                return z3.BoolVal(False)
            if token in {"AND", "OR", "NOT", "IMPLIES", "IFF", ")"}:
                return None
            consume()
            if token not in context:
                context[token] = z3.Bool(token)
            return context[token]

        def parse_unary() -> Optional[Any]:
            if peek() == "NOT":
                consume("NOT")
                operand = parse_unary()
                return z3.Not(operand) if operand is not None else None
            return parse_primary()

        def parse_conjunction() -> Optional[Any]:
            expression = parse_unary()
            if expression is None:
                return None
            while peek() == "AND":
                consume("AND")
                right = parse_unary()
                if right is None:
                    return None
                expression = z3.And(expression, right)
            return expression

        def parse_disjunction() -> Optional[Any]:
            expression = parse_conjunction()
            if expression is None:
                return None
            while peek() == "OR":
                consume("OR")
                right = parse_conjunction()
                if right is None:
                    return None
                expression = z3.Or(expression, right)
            return expression

        def parse_implication() -> Optional[Any]:
            expression = parse_disjunction()
            if expression is None:
                return None
            if peek() == "IMPLIES":
                consume("IMPLIES")
                right = parse_implication()
                if right is None:
                    return None
                return z3.Implies(expression, right)
            return expression

        def parse_iff() -> Optional[Any]:
            expression = parse_implication()
            if expression is None:
                return None
            while peek() == "IFF":
                consume("IFF")
                right = parse_implication()
                if right is None:
                    return None
                expression = expression == right
            return expression

        try:
            parsed = parse_iff()
        except RecursionError:
            return None
        if parsed is None or position != len(tokens):
            return None
        return parsed

    def verify_logical_implication(self, premises: List[str], conclusion: str) -> Tuple[bool, str]:
        """Verifica implicação proposicional e recusa caminhos não verificáveis."""
        logical_snapshot, budget_error = self._snapshot_logical_input(premises, conclusion)
        if budget_error is not None:
            return False, budget_error
        if logical_snapshot is None:
            return False, "Não foi possível criar um snapshot seguro da implicação lógica"

        premises_snapshot, conclusion_snapshot = logical_snapshot
        if not premises_snapshot:
            return False, "Nenhuma premissa fornecida"

        atom_names: set[str] = set()
        for formula in (*premises_snapshot, conclusion_snapshot):
            tokens = self._tokenize_propositional_formula(formula)
            if not tokens or not self._is_well_formed_propositional_formula(formula):
                return False, (
                    "Fórmula fora do fragmento proposicional suportado; "
                    "a implicação não foi demonstrada"
                )
            atom_names.update(self._propositional_atom_names(tokens))
            if len(atom_names) > self._MAX_LOGICAL_ATOMS:
                return False, "Quantidade de átomos distintos excede o limite global permitido"

        if not self.has_z3:
            normalized_conclusion = conclusion_snapshot.strip()
            if normalized_conclusion and any(
                normalized_conclusion == premise.strip() for premise in premises_snapshot
            ):
                return True, "Conclusão idêntica a uma premissa (inferência sintática direta)"
            return False, "Z3 indisponível; implicação não-trivial não foi demonstrada"

        try:
            context: Dict[str, Any] = {}
            parsed_premises = [
                self._parse_propositional_formula(premise, context)
                for premise in premises_snapshot
            ]
            parsed_conclusion = self._parse_propositional_formula(conclusion_snapshot, context)
            if parsed_conclusion is None or any(premise is None for premise in parsed_premises):
                return False, (
                    "Fórmula fora do fragmento proposicional suportado; "
                    "a implicação não foi demonstrada"
                )

            solver = z3.Solver()
            solver.set(timeout=self._Z3_SOLVER_TIMEOUT_MS)
            solver.add(*parsed_premises)
            solver.add(z3.Not(parsed_conclusion))
            result = solver.check()
            if solver_result_proves_implication(result, z3.unsat):
                return True, "Implicação demonstrada formalmente (Z3: premissas e negação da conclusão são inconsistentes)"
            if result == z3.sat:
                return False, (
                    "Contraexemplo lógico encontrado: as premissas podem ser verdadeiras "
                    f"enquanto a conclusão é falsa ({solver.model()})"
                )
            return False, "Z3 retornou resultado indeterminado; implicação não foi demonstrada"
        except Exception as exc:
            return False, f"Erro na verificação lógica; implicação não foi demonstrada: {str(exc)}"

    def search_counterexamples(self, expression_str: str, var_names: List[str],
                                 test_range: range = range(-5, 6)) -> List[Dict[str, Any]]:
        """Busca contraexemplos no produto cartesiano limitado das variáveis.

        A busca é apenas uma ferramenta de falsificação: uma entrada fora do
        fragmento, com domínio excessivo ou com símbolos não declarados retorna
        uma lista vazia, sem promover qualquer conclusão positiva.
        """
        if not self.has_sympy:
            return []

        try:
            expression_ast = self._parse_restricted_algebraic_ast(
                expression_str,
                allow_relational=True,
            )
            validated_names = self._validate_counterexample_variables(var_names)
        except _RestrictedAlgebraicSyntaxError:
            return []

        if type(test_range) is not range:
            return []
        try:
            test_value_count = len(test_range)
        except OverflowError:
            return []
        if (
            test_value_count > self._MAX_COUNTEREXAMPLE_TEST_VALUES
            or any(
                abs(bound).bit_length() > self._MAX_COUNTEREXAMPLE_VALUE_BITS
                for bound in (test_range.start, test_range.stop, test_range.step)
            )
        ):
            return []

        assignment_count = 1
        for _ in validated_names:
            if (
                test_value_count
                and assignment_count > self._MAX_COUNTEREXAMPLE_ASSIGNMENTS // test_value_count
            ):
                return []
            assignment_count *= test_value_count

        if not self._algebraic_free_symbol_names(expression_ast).issubset(
            set(validated_names)
        ):
            return []

        try:
            expr = self._build_sympy_expression(expression_ast)
            symbols = [sympy.Symbol(name) for name in validated_names]
        except Exception:
            return []

        counterexamples = []
        for values in product(test_range, repeat=len(symbols)):
            substitutions = dict(zip(symbols, values))
            try:
                res = expr.subs(substitutions)
                # A expressão só é registrada quando a falsidade é inequívoca;
                # ausência de avaliação nunca é tratada como contraexemplo.
                if res is False or res is sympy.false:
                    counterexample = {
                        symbol.name: value for symbol, value in zip(symbols, values)
                    }
                    counterexample["result"] = False
                    counterexamples.append(counterexample)
            except (MemoryError, OverflowError, RecursionError):
                return []
            except Exception:
                continue

        return counterexamples

    @staticmethod
    def _invalid_proof_steps_result(claim: Any, error: str) -> FormalVerificationResult:
        """Cria uma recusa fail-closed sem acumular passos parcialmente verificados."""
        return FormalVerificationResult(
            claim=claim if type(claim) is str else "",
            is_valid=False,
            confidence=0.0,
            verified_steps=[],
            errors=[error],
            algebraic_equivalent=False,
            logic_satisfiable=False,
        )

    @staticmethod
    def _invalid_proof_steps_diagnostics_result(
        claim: str,
        step_snapshots: Tuple[Tuple[str, str], ...],
        error: str,
    ) -> FormalVerificationResult:
        """Mantém diagnósticos legados sem promover nenhum passo a verificado."""
        return FormalVerificationResult(
            claim=claim,
            is_valid=False,
            confidence=0.0,
            verified_steps=[
                VerificationStep(
                    step_id=index,
                    statement=statement,
                    justification=justification,
                    is_valid=False,
                    details=error,
                )
                for index, (statement, justification) in enumerate(step_snapshots, start=1)
            ],
            errors=[error],
            algebraic_equivalent=False,
            logic_satisfiable=False,
        )

    @classmethod
    def _snapshot_proof_steps(
        cls,
        claim: Any,
        steps: Any,
    ) -> Tuple[Optional[Tuple[str, Tuple[Tuple[str, str], ...]]], Optional[str]]:
        """Valida orçamento e cria a única visão consumível do lote de prova.

        ``list``, ``dict`` e os dois campos textuais precisam ser objetos
        nativos exatos. Depois da validação, as strings nativas (imutáveis) são
        guardadas em tuplas; a fase de análise jamais relê a lista ou os
        dicionários fornecidos pelo chamador.
        """
        if type(steps) is not list:
            return None, "Os passos de prova devem ser fornecidos em uma lista nativa estrita"
        if type(claim) is not str:
            return None, "A alegação principal deve ser uma string nativa estrita"

        step_count = len(steps)
        if step_count > cls._MAX_PROOF_STEPS:
            return None, "Quantidade de passos de prova excede o limite global permitido"

        aggregate_length = len(claim)
        if aggregate_length > cls._MAX_PROOF_AGGREGATE_TEXT_LENGTH:
            return None, "Tamanho agregado da prova excede o limite global permitido"

        snapshot_steps: List[Tuple[str, str]] = []
        for step_index in range(step_count):
            try:
                step_data = steps[step_index]
            except IndexError:
                return None, "A lista de passos foi alterada durante a validação"
            if type(step_data) is not dict:
                return None, "Cada passo de prova deve ser um dicionário nativo estrito"

            statement = step_data.get("statement")
            justification = step_data.get("justification")
            if type(statement) is not str or type(justification) is not str:
                return None, (
                    "Os campos statement e justification devem ser strings nativas estritas"
                )

            for field_value in (statement, justification):
                aggregate_length += len(field_value)
                if aggregate_length > cls._MAX_PROOF_AGGREGATE_TEXT_LENGTH:
                    return None, "Tamanho agregado da prova excede o limite global permitido"
            snapshot_steps.append((statement, justification))

        return (claim, tuple(snapshot_steps)), None

    @classmethod
    def _proof_steps_budget_error(cls, claim: Any, steps: Any) -> Optional[str]:
        """Mantém a consulta de orçamento compatível com o snapshot estrito."""
        _, error = cls._snapshot_proof_steps(claim, steps)
        return error

    def verify_proof_steps(self, claim: str, steps: List[Dict[str, str]]) -> FormalVerificationResult:
        """Verifica uma sequência ordenada de passos de prova."""
        proof_snapshot, budget_error = self._snapshot_proof_steps(claim, steps)
        if budget_error is not None:
            return self._invalid_proof_steps_result(claim, budget_error)
        if proof_snapshot is None:
            return self._invalid_proof_steps_result(
                claim,
                "Não foi possível criar um snapshot seguro dos passos de prova",
            )

        claim_snapshot, step_snapshots = proof_snapshot
        try:
            _, _, canonical_claim = self._parse_restricted_algebraic_equation(
                claim_snapshot
            )
        except _RestrictedAlgebraicSyntaxError as exc:
            claim_error = (
                "A alegação principal é uma igualdade algébrica malformada ou "
                f"restrita: {exc}"
            )
            # R448 expõe, no modo sem SymPy, os passos já capturados como
            # diagnósticos inválidos. Eles não participam de nenhuma promoção
            # de prova e continuam provenientes exclusivamente do snapshot.
            if not self.has_sympy:
                return self._invalid_proof_steps_diagnostics_result(
                    claim_snapshot,
                    step_snapshots,
                    claim_error,
                )
            return self._invalid_proof_steps_result(claim_snapshot, claim_error)

        verified_steps: List[VerificationStep] = []
        all_valid = True
        errors: List[str] = []
        sympy_count = 0
        claim_established = False

        for i, (stmt, just) in enumerate(step_snapshots, start=1):
            is_valid = False
            details = "Passo ainda não verificado"
            step_sympy = False
            step_z3 = False

            # Somente igualdades algébricas do fragmento restrito podem ser
            # promovidas a passos verificados.
            if "=" in stmt:
                try:
                    lhs, rhs, canonical_step = self._parse_restricted_algebraic_equation(
                        stmt
                    )
                except _RestrictedAlgebraicSyntaxError as exc:
                    all_valid = False
                    details = f"Equação algébrica recusada: {exc}"
                    errors.append(f"Passo {i}: {details}")
                else:
                    ok, msg = self.verify_algebraic_identity(lhs, rhs)
                    if ok:
                        is_valid = True
                        step_sympy = True
                        sympy_count += 1
                        details = msg
                        if canonical_step == canonical_claim:
                            claim_established = True
                    else:
                        all_valid = False
                        details = msg
                        errors.append(f"Passo {i}: {msg}")
            else:
                if not stmt.strip():
                    all_valid = False
                    errors.append(f"Passo {i}: Declaração vazia")
                else:
                    all_valid = False
                    details = (
                        "Afirmação declarativa sem derivação formal verificável; "
                        "permanece pendente"
                    )
                    errors.append(f"Passo {i}: {details}")

            verified_steps.append(
                VerificationStep(
                    step_id=i,
                    statement=stmt,
                    justification=just,
                    is_valid=is_valid,
                    details=details,
                    sympy_verified=step_sympy,
                    z3_verified=step_z3,
                )
            )

        # A validade local de um passo não estabelece, por si só, a alegação
        # principal. A comparação usa somente a forma estrutural das ASTs
        # restritas previamente validadas, e não normalização textual.
        if not claim_established:
            all_valid = False
            errors.append(
                "A alegação principal não foi estabelecida por um passo formalmente verificado"
            )

        confidence = 0.0
        if all_valid and verified_steps:
            confidence = 0.99 if sympy_count == len(verified_steps) else 0.95

        return FormalVerificationResult(
            claim=claim_snapshot,
            is_valid=all_valid and len(verified_steps) > 0,
            confidence=confidence,
            verified_steps=verified_steps,
            errors=errors,
            algebraic_equivalent=(sympy_count > 0),
            logic_satisfiable=all_valid,
        )
