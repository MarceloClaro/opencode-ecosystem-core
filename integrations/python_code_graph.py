"""R896: relações Python declaradas, sem importar ou executar o corpus.

Resolução deliberadamente conservadora: atributos de instâncias, wrappers,
reatribuições e namespaces ambíguos permanecem desconhecidos. Este módulo
recebe somente snapshots de bytes; não lê caminhos nem inicia processos.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

GRAPH_TOOLS = ("get_symbol_usages", "get_call_tree", "get_blast_radius")
MAX_AST_NODES = 2_000_000
MAX_CALLS = 150_000
MAX_RESPONSE_NODES = 1000
MAX_RESPONSE_BYTES = 48_000
MAX_FACTS = 300_000
_DYNAMIC_CALLS = {"getattr", "setattr", "delattr", "eval", "exec", "__import__", "globals", "locals"}


@dataclass
class _Scope:
    kind: str
    qualname: str
    owner: str
    parent: Any = None
    bindings: dict = field(default_factory=lambda: defaultdict(list))
    wildcard: bool = False
    unsupported: str | None = None


def _path(value):
    if not isinstance(value, str) or not value or len(value) > 4096:
        raise ValueError("invalid_source_path")
    path = PurePosixPath(value)
    if (path.is_absolute() or ".." in path.parts or path.as_posix() != value
            or "\\" in value or ":" in value or any(ord(c) < 32 for c in value)):
        raise ValueError("invalid_source_path")
    return path


def _module(path):
    parts = list(PurePosixPath(path).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _expression(node):
    pieces = []
    while isinstance(node, ast.Attribute) and len(pieces) < 12:
        pieces.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        return ".".join([node.id, *reversed(pieces)])[:200]
    return "<" + type(node).__name__ + ">"


def _find_cycles(facts, selected):
    """DFS iterativa sobre o subgrafo, independente do caminho escolhido no BFS."""
    adjacent = defaultdict(set)
    for fact in facts:
        adjacent[fact["source_id"]].add(fact["target_id"])
    color, cycles = {}, []
    for start in sorted(selected):
        if color.get(start):
            continue
        color[start] = 1
        path, positions = [start], {start: 0}
        stack = [(start, iter(sorted(adjacent[start])))]
        while stack:
            current, following_nodes = stack[-1]
            following = next(following_nodes, None)
            if following is None:
                color[current] = 2
                stack.pop()
                positions.pop(current)
                path.pop()
            elif color.get(following) == 1:
                cycles.append({"path": [*path[positions[following]:], following]})
                if len(cycles) > 50:
                    return cycles[:50], True
            elif not color.get(following):
                color[following] = 1
                positions[following] = len(path)
                path.append(following)
                stack.append((following, iter(sorted(adjacent[following]))))
    return cycles, False


class _Declarations(ast.NodeVisitor):
    def __init__(self, graph, unit):
        self.graph, self.unit = graph, unit
        self.scope = unit["scope"]

    def _definition(self, node, kind):
        self.graph.check()
        parent = self.scope
        qualname = ".".join(filter(None, (parent.qualname, node.name)))
        canonical = self.unit["path"] + "::" + qualname
        self.graph.definitions[canonical].append(self.graph.symbol(self.unit, canonical, qualname, kind, node))
        parent.bindings[node.name].append(("symbol", canonical, bool(node.decorator_list)))
        # Defaults, decorators, bases and annotations are declaration context,
        # never attributed to the body of the function being declared.
        expressions = list(node.decorator_list)
        if isinstance(node, ast.ClassDef):
            expressions += list(node.bases) + [keyword.value for keyword in node.keywords]
        else:
            expressions += list(node.args.defaults) + [item for item in node.args.kw_defaults if item is not None]
            expressions += [arg.annotation for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
                            if arg.annotation is not None]
            if node.returns is not None:
                expressions.append(node.returns)
        self.unit["declaration_expressions"][id(node)] = expressions
        for item in expressions:
            self.visit(item)
        child = _Scope(kind, qualname, canonical, parent)
        self.unit["scopes"][id(node)] = child
        self.scope = child
        for parameter in getattr(node, "type_params", []):
            child.bindings[parameter.name].append(("unknown", "type_parameter"))
        if not isinstance(node, ast.ClassDef):
            for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs,
                        *([node.args.vararg] if node.args.vararg else []),
                        *([node.args.kwarg] if node.args.kwarg else [])):
                child.bindings[arg.arg].append(("unknown", "shadowed_or_rebound"))
        for statement in node.body:
            self.visit(statement)
        self.scope = parent

    def visit_FunctionDef(self, node):
        self._definition(node, "function")

    def visit_AsyncFunctionDef(self, node):
        self._definition(node, "async_function")

    def visit_ClassDef(self, node):
        self._definition(node, "class")

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.scope.bindings[node.id].append(("unknown", "shadowed_or_rebound"))

    def visit_Attribute(self, node):
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            current = node
            while isinstance(current, ast.Attribute):
                current = current.value
            if isinstance(current, ast.Name):
                self.scope.bindings[current.id].append(("unknown", "attribute_write"))
        self.generic_visit(node)

    def visit_NamedExpr(self, node):
        # PEP 572 binds a comprehension's walrus target in the containing
        # scope, unlike ordinary comprehension targets.
        target_scope = self.scope
        while target_scope.unsupported == "unsupported_comprehension" and target_scope.parent is not None:
            target_scope = target_scope.parent
        if isinstance(node.target, ast.Name):
            target_scope.bindings[node.target.id].append(("unknown", "shadowed_or_rebound"))
        self.visit(node.value)

    def visit_Import(self, node):
        for alias in node.names:
            self.scope.bindings[alias.asname or alias.name.split(".")[0]].append(
                ("module", alias.name if alias.asname else alias.name.split(".")[0]))

    def visit_ImportFrom(self, node):
        module = node.module or ""
        if node.level:
            package = self.unit["module"].split(".")
            if PurePosixPath(self.unit["path"]).name != "__init__.py":
                package = package[:-1]
            if node.level > len(package):
                module = "<invalid_relative_import>"
            else:
                module = ".".join([*package[:len(package) - node.level + 1], *([module] if module else [])])
        for alias in node.names:
            if alias.name == "*":
                self.scope.wildcard = True
            else:
                self.scope.bindings[alias.asname or alias.name].append(("import", module, alias.name))

    def visit_Global(self, node):
        for name in node.names:
            self.scope.bindings[name].append(("unknown", "global_or_nonlocal"))

    visit_Nonlocal = visit_Global

    def visit_ExceptHandler(self, node):
        if node.name:
            self.scope.bindings[node.name].append(("unknown", "exception_binding"))
        self.generic_visit(node)

    def visit_MatchAs(self, node):
        if node.name:
            self.scope.bindings[node.name].append(("unknown", "pattern_binding"))
        self.generic_visit(node)

    visit_MatchStar = visit_MatchAs

    def visit_MatchMapping(self, node):
        if node.rest:
            self.scope.bindings[node.rest].append(("unknown", "pattern_binding"))
        self.generic_visit(node)

    def _unsupported(self, node, reason):
        parent = self.scope
        self.scope = _Scope("unsupported", parent.qualname, parent.owner, parent, unsupported=reason)
        self.unit["scopes"][id(node)] = self.scope
        self.generic_visit(node)
        self.scope = parent

    def visit_Lambda(self, node):
        self._unsupported(node, "unsupported_lambda")

    def visit_ListComp(self, node):
        self._unsupported(node, "unsupported_comprehension")

    visit_SetComp = visit_ListComp
    visit_DictComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp


class _References(ast.NodeVisitor):
    def __init__(self, graph, unit):
        self.graph, self.unit, self.scope = graph, unit, unit["scope"]
        self.callee_nodes = set()

    def _definition(self, node):
        for expression in self.unit["declaration_expressions"][id(node)]:
            self.visit(expression)
        parent, self.scope = self.scope, self.unit["scopes"][id(node)]
        for statement in node.body:
            self.visit(statement)
        self.scope = parent

    visit_FunctionDef = _definition
    visit_AsyncFunctionDef = _definition
    visit_ClassDef = _definition

    def _unsupported(self, node):
        parent, self.scope = self.scope, self.unit["scopes"][id(node)]
        self.generic_visit(node)
        self.scope = parent

    visit_Lambda = _unsupported
    visit_ListComp = _unsupported
    visit_SetComp = _unsupported
    visit_DictComp = _unsupported
    visit_GeneratorExp = _unsupported

    def _record(self, expression, node, kind):
        self.graph.reference_visits += 1
        if self.graph.reference_visits % 1000 == 0:
            self.graph.check()
        target, reason = self.graph.resolve(expression, self.scope)
        location = {"file_path": self.unit["path"], "source_sha256": self.unit["sha256"],
                    "start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno),
                    "column": node.col_offset, "caller_id": self.scope.owner}
        if target:
            self.graph.add_fact({**location, "source_id": self.scope.owner, "target_id": target, "kind": kind})
        else:
            self.graph.unresolved_count += 1
            self.graph.unresolved_counts[self.scope.owner] += 1
            rows = self.graph.unresolved[self.scope.owner]
            if len(rows) < 50:
                rows.append({**location, "expression": _expression(expression), "kind": kind, "reason": reason})

    def visit_Call(self, node):
        self._record(node.func, node, "call")
        self.callee_nodes.add(id(node.func))
        self.visit(node.func)
        for item in node.args:
            self.visit(item)
        for keyword in node.keywords:
            self.visit(keyword.value)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and id(node) not in self.callee_nodes:
            self._record(node, node, "reference")

    def visit_Attribute(self, node):
        if isinstance(node.ctx, ast.Load) and id(node) not in self.callee_nodes:
            self._record(node, node, "reference")
        # Preserve calls such as factory().method(), but do not count the
        # namespace base of module.function() as another function usage.
        current = node.value
        while isinstance(current, ast.Attribute):
            current = current.value
        if not isinstance(current, ast.Name):
            self.visit(current)

    def visit_Import(self, node):
        pass

    visit_ImportFrom = visit_Import


class _Graph:
    def __init__(self, files, timeout):
        self.deadline = time.monotonic() + min(timeout, 30)
        self.definitions = defaultdict(list)
        self.modules = defaultdict(list)
        self.units, self.parse_errors, self.facts = [], [], []
        self.unresolved = defaultdict(list)
        self.unresolved_counts = defaultdict(int)
        self.unresolved_count = self.ast_nodes = self.call_count = 0
        self.reference_visits = 0
        self.by_source, self.by_target = defaultdict(list), defaultdict(list)
        self.files = files
        if not isinstance(files, dict) or len(files) > 2000:
            raise ValueError("invalid_or_oversized_corpus")
        total = 0
        for path, info in sorted(files.items()):
            parsed_path = _path(path)
            raw = info.get("_data") if isinstance(info, dict) else None
            if (not isinstance(raw, bytes) or len(raw) > 512 * 1024 or type(info.get("bytes")) is not int or info["bytes"] != len(raw)
                    or info.get("sha256") != hashlib.sha256(raw).hexdigest()):
                raise ValueError("source_snapshot_hash_or_size_mismatch")
            total += len(raw)
            if total > 32 * 1024 * 1024:
                raise ValueError("corpus_byte_limit")
            if parsed_path.suffix != ".py":
                continue
            self.check()
            try:
                text = raw.decode("utf-8-sig")
                tree = ast.parse(text, filename=path)
                for item in ast.walk(tree):
                    self.ast_nodes += 1
                    self.call_count += isinstance(item, ast.Call)
                    if self.ast_nodes % 1000 == 0:
                        self.check()
                    if self.ast_nodes > MAX_AST_NODES or self.call_count > MAX_CALLS:
                        raise ValueError("ast_or_call_budget_exceeded")
                module = _module(path)
                canonical = path + "::<module>"
                unit = {"path": path, "sha256": info["sha256"], "text": text, "module": module,
                        "lines": text.splitlines(),
                        "tree": tree, "scopes": {}, "declaration_expressions": {},
                        "scope": _Scope("module", "", canonical)}
                self.modules[module].append(path)
                self.definitions[canonical].append(self.symbol(unit, canonical, "<module>", "module", None))
                _Declarations(self, unit).visit(tree)
                self.units.append(unit)
            except (SyntaxError, UnicodeError, RecursionError) as exc:
                for canonical in list(self.definitions):
                    if canonical.startswith(path + "::"):
                        del self.definitions[canonical]
                for paths in self.modules.values():
                    if path in paths:
                        paths.remove(path)
                self.parse_errors.append({"file_path": path, "source_sha256": info["sha256"],
                    "start_line": getattr(exc, "lineno", None), "reason": type(exc).__name__})
        for unit in self.units:
            self.check()
            _References(self, unit).visit(unit["tree"])

    def check(self):
        if time.monotonic() > self.deadline:
            raise TimeoutError("python_graph_deadline_exceeded")

    def symbol(self, unit, canonical, qualified, kind, node):
        lines = unit["lines"]
        line = node.lineno if node is not None else 1
        return {"symbol_id": canonical, "file_path": unit["path"], "source_sha256": unit["sha256"],
                "name": qualified.rsplit(".", 1)[-1], "qualified_name": qualified, "kind": kind,
                "language": "python", "module": unit["module"], "start_line": line,
                "end_line": getattr(node, "end_lineno", max(1, len(lines))),
                "signature": (lines[line - 1].strip() if lines else "")[:300]}

    def add_fact(self, fact):
        if len(self.facts) >= MAX_FACTS:
            raise ValueError("reference_budget_exceeded")
        self.facts.append(fact)
        self.by_source[fact["source_id"]].append(fact)
        self.by_target[fact["target_id"]].append(fact)
        if len(self.facts) % 1000 == 0:
            self.check()

    def _binding(self, scope, name):
        current = scope
        while current is not None:
            if current.unsupported:
                return None, current.unsupported
            if current.wildcard:
                return None, "wildcard_import"
            bindings = current.bindings.get(name, [])
            if bindings:
                if len(bindings) != 1:
                    return None, "shadowed_or_rebound"
                binding = bindings[0]
                return (None, binding[1]) if binding[0] == "unknown" else (binding, None)
            previous, current = current, current.parent
            if previous.kind in {"function", "async_function", "class"}:
                while current is not None and current.kind == "class":
                    current = current.parent
        return None, "unbound_or_external_name"

    def _target(self, canonical, decorated=False):
        if decorated:
            return None, "decorated_symbol"
        rows = self.definitions.get(canonical, [])
        if len(rows) != 1:
            return None, "ambiguous_or_external_import"
        return canonical, None

    def _import_target(self, module, member):
        paths = self.modules.get(module, [])
        if module + "." + member in self.modules:
            return None, "ambiguous_or_external_import"
        candidates = [path + "::" + member for path in paths if path + "::" + member in self.definitions]
        if len(candidates) != 1 or len(paths) != 1:
            return None, "ambiguous_or_external_import"
        # A decorated exported symbol retains a declaration, not its original
        # callable identity. Consult its binding instead of assuming the wrapper.
        unit = next(unit for unit in self.units if unit["path"] == paths[0])
        if unit["scope"].wildcard:
            return None, "wildcard_import"
        bindings = unit["scope"].bindings.get(member, [])
        if len(bindings) != 1 or bindings[0][0] != "symbol":
            return None, "shadowed_or_rebound"
        return self._target(candidates[0], bindings[0][2])

    def resolve(self, expression, scope):
        if scope.unsupported:
            return None, scope.unsupported
        if isinstance(expression, ast.Name):
            if expression.id in _DYNAMIC_CALLS:
                return None, "dynamic_call"
            binding, reason = self._binding(scope, expression.id)
            if binding is None:
                return None, reason
            if binding[0] == "symbol":
                return self._target(binding[1], binding[2])
            if binding[0] == "import":
                return self._import_target(binding[1], binding[2])
            return None, "module_is_not_a_symbol"
        if not isinstance(expression, ast.Attribute):
            return None, "dynamic_call"
        parts, current = [], expression
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if not isinstance(current, ast.Name):
            return None, "dynamic_attribute"
        binding, reason = self._binding(scope, current.id)
        if binding is None:
            return None, "dynamic_attribute" if reason == "unbound_or_external_name" else reason
        if binding[0] == "module":
            prefix = binding[1]
        elif binding[0] == "import":
            prefix = binding[1] + "." + binding[2]
            # from package import member may denote a function or a submodule.
            symbol, _ = self._import_target(binding[1], binding[2])
            has_declared_member = any(path + "::" + binding[2] in self.definitions
                                      for path in self.modules.get(binding[1], []))
            if symbol or has_declared_member or prefix not in self.modules:
                return None, "dynamic_attribute"
        else:
            return None, "dynamic_attribute"
        parts.reverse()
        module = ".".join([prefix, *parts[:-1]])
        return self._import_target(module, parts[-1])

    def select(self, selector):
        if "::" in selector:
            path, _ = selector.split("::", 1)
            suffix = _path(path).suffix
            if suffix != ".py":
                return [], "unsupported_language"
            if any(error["file_path"] == path for error in self.parse_errors):
                return [], "syntax_error_target"
            rows = self.definitions.get(selector, [])
        else:
            rows = [symbol for values in self.definitions.values() for symbol in values
                    if selector in {symbol["name"], symbol["qualified_name"],
                                    symbol["module"] + "." + symbol["qualified_name"]}]
        if len(rows) > 1:
            return rows[:20], "ambiguous_symbol"
        return rows, "completed" if rows else "symbol_not_found"

    def query(self, tool, arguments):
        selector = arguments["symbol_name"]
        base = {"ok": False, "status": "completed", "backend": "core_python_ast", "schema_version": "r896.v1",
                "static_only": True, "tool": tool, "requested_symbol": selector,
                "scope": "tracked_python_source_snapshot", "coverage_complete": False,
                "symbols": [], "edges": [], "usages": [], "cycles": [], "unresolved": [],
                "parse_errors": self.parse_errors[:20], "parse_error_count": len(self.parse_errors),
                "truncated": False, "truncation_reasons": [], "depth_limited": False,
                "limits": {"max_ast_nodes": MAX_AST_NODES, "max_calls": MAX_CALLS,
                           "max_response_nodes": MAX_RESPONSE_NODES, "max_response_bytes": MAX_RESPONSE_BYTES,
                           "max_depth": 3, "timeout_seconds_cap": 30},
                "coverage": {"selected_files": len(self.files), "parsed_python_files": len(self.units),
                             "non_python_files": sum(not path.endswith(".py") for path in self.files),
                             "ast_nodes": self.ast_nodes, "call_sites": self.call_count,
                             "resolved_reference_sites": len(self.facts), "unresolved_sites": self.unresolved_count},
                "limitations": ["Relações declaradas; não comprovam execução, completude dinâmica ou ausência de falhas.",
                                "self/instâncias, wrappers, wildcard, aliases por atribuição e resolução de atributos dinâmicos não são inferidos.",
                                "Imports consideram o caminho relativo à raiz, sem adivinhar PYTHONPATH ou layouts src."]}
        if not self.units:
            base["status"] = ("syntax_error_target" if self.parse_errors else
                              "unsupported_language" if base["coverage"]["non_python_files"] else "empty_python_corpus")
            return base
        rows, status = self.select(selector)
        if status != "completed":
            base.update(status=status, candidates=rows)
            return base
        root = rows[0]["symbol_id"]
        selected, facts, cycles, inspected = {root}, [], [], set()
        if tool == "get_symbol_usages":
            inspected.add(root)
            for fact in self.by_target[root]:
                if len(selected) >= MAX_RESPONSE_NODES and fact["source_id"] not in selected:
                    base["truncation_reasons"].append("node_limit")
                    continue
                selected.add(fact["source_id"])
                inspected.add(fact["source_id"])
                facts.append(fact)
                if len(facts) >= 3000:
                    base["truncation_reasons"].append("edge_limit")
                    break
            base["usages"] = facts.copy()
        else:
            reverse = tool == "get_blast_radius" or arguments.get("direction", "callees") == "callers"
            depth = arguments.get("depth", 2 if tool == "get_blast_radius" else 1)
            base.update(direction="callers" if reverse else "callees", depth=depth,
                        relation_scope="calls_and_symbol_references" if tool == "get_blast_radius" else "calls_only")
            pending, best = deque([(root, 0, (root,))]), {root: 0}
            seen_facts = set()
            while pending:
                self.check()
                current, distance, path = pending.popleft()
                adjacent = (self.by_target if reverse else self.by_source)[current]
                adjacent = [fact for fact in adjacent if tool == "get_blast_radius" or fact["kind"] == "call"]
                if distance >= depth:
                    base["depth_limited"] |= bool(adjacent)
                    continue
                inspected.add(current)
                for fact in adjacent:
                    following = fact["source_id"] if reverse else fact["target_id"]
                    if len(selected) >= MAX_RESPONSE_NODES and following not in selected:
                        base["truncation_reasons"].append("node_limit")
                        continue
                    selected.add(following)
                    identity = (fact["source_id"], fact["target_id"], fact["file_path"], fact["start_line"], fact["column"], fact["kind"])
                    if identity not in seen_facts:
                        seen_facts.add(identity)
                        facts.append(fact)
                    if following in path:
                        index = path.index(following)
                        cycles.append({"path": [*path[index:], following]})
                    elif following not in best or best[following] > distance + 1:
                        best[following] = distance + 1
                        pending.append((following, distance + 1, (*path, following)))
                    if len(facts) >= 3000:
                        base["truncation_reasons"].append("edge_limit")
                        pending.clear()
                        break
        cycles, cycles_truncated = _find_cycles(facts, selected)
        base.update(ok=True, target_symbol_id=root, symbols=[rows[0], *[self.definitions[key][0] for key in sorted(selected - {root})]],
                    edges=facts, cycles=cycles, cycle_detection_scope="returned_static_subgraph",
                    unresolved=[row for key in sorted(inspected) for row in self.unresolved[key]][:100])
        base["unresolved_scope_count"] = sum(self.unresolved_counts[key] for key in inspected)
        if base["unresolved_scope_count"] > len(base["unresolved"]):
            base["truncation_reasons"].append("unresolved_sample_limit")
        if cycles_truncated:
            base["truncation_reasons"].append("cycle_sample_limit")
        if tool == "get_blast_radius":
            base["affected_symbol_ids"] = sorted(selected - {root})
            base["affected_count"] = len(base["affected_symbol_ids"])
        self._bound(base)
        base["unresolved_sample_count"] = len(base["unresolved"])
        base["unresolved_sample_truncated"] = base["unresolved_scope_count"] > len(base["unresolved"])
        base["truncated"] = bool(base["truncation_reasons"])
        base["coverage_complete"] = not (self.parse_errors or self.unresolved_count or base["truncated"]
                                              or base["depth_limited"] or base["coverage"]["non_python_files"])
        if tool == "get_blast_radius":
            base["affected_count_is_lower_bound"] = not base["coverage_complete"]
        return base

    @staticmethod
    def _bound(base):
        # Every removed endpoint also removes its edges/usages: a truncated
        # presentation must not invent a complete or dangling graph.
        while len(json.dumps(base, ensure_ascii=True).encode()) > MAX_RESPONSE_BYTES:
            base["truncation_reasons"] = list(set(base["truncation_reasons"]) | {"response_byte_limit"})
            if len(base["unresolved"]) > 10:
                base["unresolved"] = base["unresolved"][:len(base["unresolved"]) // 2]
            elif len(base["symbols"]) > 1:
                base["symbols"] = base["symbols"][:max(1, len(base["symbols"]) // 2)]
            else:
                for key in ("edges", "usages", "unresolved", "cycles"):
                    base[key] = base[key][:len(base[key]) // 2]
            ids = {row["symbol_id"] for row in base["symbols"]}
            base["edges"] = [row for row in base["edges"] if row["source_id"] in ids and row["target_id"] in ids]
            base["usages"] = [row for row in base["usages"] if row["source_id"] in ids and row["target_id"] in ids]
            base["cycles"] = [row for row in base["cycles"] if set(row["path"]) <= ids]
            base["unresolved"] = [row for row in base["unresolved"] if row["caller_id"] in ids]
            if "affected_symbol_ids" in base:
                base["affected_symbol_ids"] = sorted(ids - {base["target_symbol_id"]})
                base["affected_count"] = len(base["affected_symbol_ids"])
        base["truncation_reasons"] = sorted(set(base["truncation_reasons"]))


def analyze_python_graph(files: dict, tool: str, arguments: dict, *, timeout_seconds: float = 30) -> dict:
    """Resolve uma consulta sobre bytes conferidos; não acessa a rede/arquivos."""
    if tool not in GRAPH_TOOLS or not isinstance(arguments, dict):
        raise ValueError("invalid_python_graph_tool")
    allowed = {"symbol_name"}
    if tool != "get_symbol_usages":
        allowed.add("depth")
    if tool == "get_call_tree":
        allowed.add("direction")
    name = arguments.get("symbol_name")
    if (set(arguments) - allowed or not isinstance(name, str) or not name.strip() or len(name) > 2000
            or any(ord(c) < 32 for c in name)):
        raise ValueError("invalid_python_graph_arguments")
    if "depth" in arguments and (type(arguments["depth"]) is not int
            or not (1 if tool == "get_blast_radius" else 0) <= arguments["depth"] <= 3):
        raise ValueError("invalid_python_graph_depth")
    if arguments.get("direction", "callees") not in {"callers", "callees"}:
        raise ValueError("invalid_python_graph_direction")
    if type(timeout_seconds) not in (int, float) or not math.isfinite(timeout_seconds) or not 0 < timeout_seconds <= 120:
        raise ValueError("invalid_python_graph_timeout")
    return _Graph(files, timeout_seconds).query(tool, arguments)
