#!/usr/bin/env python3
"""R879: inventário estático de um snapshot Git, sem executar suas fontes.

O grafo Python registra imports declarados. Não mede qualidade, cobertura de
testes, prontidão de motores ou caminhos executados. As superfícies TS/JS/Lean
usam extração lexical explicitamente limitada. Nenhum valor de ambiente,
credencial, prompt ou comando da configuração é exportado.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

DOMAIN_ROOTS = frozenset({"artigos", "odonto", "prestacao_contas_nota_dez", "livro-core", "livro-alfabetizacao", "manuscrito_porescrito799_R522", "publications", "producao_cientifica", "pesquisa-artigo-qualis-a1", "validacao_externa", "notebooks", "illustrations", "assets", "data", "Medicina", "medicos", "contas-escolares-airam-veras", "PLUGIN NOTA10", "Nova pasta"})
DOMAIN_FILES = frozenset({"build_livro_tritemo.py", "enriquecer_notebook.py", "enriquecer_notebook_v2.py", "gerar_artigo_expandido.py", "gerar_fichamento_pdf.py", "gerar_notebook_didatico.py", "gerar_notebook_final.py", "regenerar_figuras.py", "regenerar_figuras_v2.py", "update_notebook.py"})
LANGUAGES = {".py": "python", ".ts": "typescript", ".tsx": "typescript", ".js": "javascript", ".jsx": "javascript", ".lean": "lean"}
LAYERS = {
    "marceloclaro": "orquestracao", "nano_orchestration": "orquestracao",
    "agents": "agentes", "agent_runners": "agentes", "protocolos": "protocolos",
    "mci": "memoria_e_evidencias", "trust": "governanca", "governanca": "governanca",
    "sdd": "governanca", "economy": "governanca", "gametheory": "governanca",
    "reasoning": "raciocinio", "reversa_universal": "engenharia_reversa",
    "reversa_feynman": "engenharia_reversa", "integrations": "integracoes",
    "infra_dados": "infraestrutura", "scanners": "diagnostico", "evolution": "evolucao",
    "webapp": "interfaces", "scripts": "ferramentas", "rag": "pesquisa_e_rag",
    "research": "pesquisa_e_rag", "research_factory": "pesquisa_e_rag",
    "agentic_science_v2": "pesquisa_e_rag", "scientific_lab": "pesquisa_e_rag",
    "academic": "pesquisa_e_rag", "publishing": "publicacao", "plugins": "plugins",
    ".opencode": "interfaces", "skills": "skills",
}


def classify(path: str) -> str:
    """Classificação explícita por finalidade e localização, não por qualidade."""
    parts = PurePosixPath(path).parts
    root = parts[0]
    lower = path.lower()
    if any(part.lower() in {"vendor", "vendored", "node_modules"} for part in parts) or lower.startswith(".opencode/scientific-plugins/packages/"):
        return "vendor"
    if root in {".backups", "tmp"} or any(part.lower() in {"snapshot", "snapshots", "baseline", "baselines"} for part in parts) or lower.startswith(("docs/evidence/", "docs/evidencias-", ".opencode/scientific-plugins/")):
        return "historical_snapshot"
    if root == "tests" or any(part in {"tests", "test"} for part in parts[:-1]) or PurePosixPath(path).name.startswith("test_"):
        return "test"
    if root in {"examples", "exemplos", "benchmarks"}:
        return "example"
    if root == "templates":
        return "template"
    if root == "outputs":
        return "evidence_output"
    if root in DOMAIN_ROOTS or path in DOMAIN_FILES:
        return "domain_artifact"
    if root in {"docs", "specs"} or PurePosixPath(path).suffix.lower() in {".md", ".rst", ".txt", ".html", ".mmd", ".svg"}:
        return "documentation"
    if root in {".github", ".evolve", ".antigravity", ".claude"} or PurePosixPath(path).name in {"opencode.json", "opencode.local.jsonc", "tui.json", "pytest.ini", "setup.cfg", "package.json", "package-lock.json", "tsconfig.json"}:
        return "configuration"
    if PurePosixPath(path).suffix.lower() in LANGUAGES or PurePosixPath(path).suffix.lower() in {".sh", ".ps1"}:
        return "production"
    return "repository_asset"


def _git(root: Path, *args: str) -> bytes:
    try:
        return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"Falha ao ler ref Git: {exc.stderr.decode(errors='replace').strip()}") from exc


def _blob_records(root: Path, commit: str):
    """Lê blobs via cat-file, mantendo somente um blob em memória por vez."""
    listing = _git(root, "ls-tree", "-rz", "--full-tree", commit)
    process = subprocess.Popen(["git", "-C", str(root), "cat-file", "--batch"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for record in listing.split(b"\0"):
            if not record:
                continue
            metadata, raw_path = record.split(b"\t", 1)
            mode, kind, oid = metadata.decode("ascii").split()
            path = raw_path.decode("utf-8", errors="surrogateescape")
            if kind != "blob":
                yield path, mode, kind, oid, None
                continue
            process.stdin.write(oid.encode("ascii") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline().decode("ascii").split()
            if len(header) != 3 or header[1] != "blob":
                raise ValueError(f"Objeto Git inesperado para {path}")
            data = process.stdout.read(int(header[2]))
            if len(data) != int(header[2]) or process.stdout.read(1) != b"\n":
                raise ValueError(f"Blob incompleto para {path}")
            yield path, mode, kind, oid, data
    finally:
        process.stdin.close()
        process.stdout.close()
        process.stderr.close()
        process.wait(timeout=10)


def _module_name(path: str) -> str:
    parts = list(PurePosixPath(path).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _node_id(value: str) -> str:
    return "n_" + hashlib.sha256(value.encode("utf-8", errors="surrogateescape")).hexdigest()[:20]


def _symbols(tree: ast.AST) -> list[dict]:
    result = []

    def visit(node, prefix=""):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                kind = "class" if isinstance(child, ast.ClassDef) else "async_function" if isinstance(child, ast.AsyncFunctionDef) else "function"
                result.append({"name": name, "kind": kind, "line": child.lineno, "end_line": child.end_lineno})
                visit(child, name + ".")
            else:
                visit(child, prefix)

    visit(tree)
    return sorted(result, key=lambda item: (item["line"], item["name"]))


def _lexical_symbols(text: str, language: str) -> list[dict]:
    pattern = r"\b(class|function)\s+([A-Za-z_$][\w$]*)" if language != "lean" else r"\b(theorem|lemma|def|structure|class|inductive|abbrev)\s+([\w'.]+)"
    return [{"name": match.group(2), "kind": match.group(1), "line": text.count("\n", 0, match.start()) + 1} for match in re.finditer(pattern, text)]


def _parse_python(snapshot: dict, texts: dict[str, str]) -> None:
    """Conecta somente módulos encontrados no snapshot; registra o restante."""
    by_name = {item["module"]: item for item in snapshot["modules"]}
    edges = []
    for module in snapshot["modules"]:
        try:
            tree = ast.parse(texts[module["path"]], filename=module["path"])
        except (SyntaxError, ValueError) as exc:
            snapshot["parse_errors"].append({"path": module["path"], "line": getattr(exc, "lineno", None), "message": str(exc)})
            continue
        module["symbols"] = _symbols(tree)
        module["classes"] = [item for item in module["symbols"] if item["kind"] == "class"]
        module["functions"] = [item for item in module["symbols"] if item["kind"] != "class"]
        package = module["module"] if module["path"].endswith("/__init__.py") else module["module"].rpartition(".")[0]
        for node in ast.walk(tree):
            candidates = []
            label = None
            if isinstance(node, ast.Import):
                candidates = [alias.name for alias in node.names]
                label = ", ".join(candidates)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    package_parts = package.split(".") if package else []
                    if node.level > len(package_parts):
                        base = None
                    else:
                        base = ".".join(package_parts[: len(package_parts) - node.level + 1])
                        if node.module:
                            base += "." + node.module
                else:
                    base = node.module or ""
                label = "." * node.level + (node.module or "")
                if base is None:
                    snapshot["external_imports"].append({"module": module["module"], "path": module["path"], "line": node.lineno, "import": label, "reason": "relative_beyond_package"})
                    continue
                candidates = [base] if base else []
                candidates.extend(f"{base}.{alias.name}" if base else alias.name for alias in node.names if alias.name != "*")
            elif isinstance(node, ast.Call):
                dynamic = isinstance(node.func, ast.Name) and node.func.id == "__import__" or isinstance(node.func, ast.Attribute) and node.func.attr == "import_module"
                if dynamic:
                    literal = node.args[0].value if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str) else None
                    snapshot["dynamic_imports"].append({"module": module["module"], "path": module["path"], "line": node.lineno, "literal_module": literal, "resolution": "not_added_to_static_edges"})
                continue
            else:
                continue
            module["imports"].append({"line": node.lineno, "declaration": label, "candidates": candidates})
            resolved = set()
            for candidate in candidates:
                target = candidate
                while target and target not in by_name:
                    target = target.rpartition(".")[0]
                if target:
                    resolved.add(target)
            if isinstance(node, ast.Import):
                for candidate in candidates:
                    if candidate not in by_name:
                        prefix_present = any(candidate.startswith(target + ".") for target in resolved)
                        snapshot["external_imports"].append({"module": module["module"], "path": module["path"], "line": node.lineno, "import": candidate, "reason": "partial_internal_prefix" if prefix_present else "not_in_production_snapshot"})
            elif not resolved:
                snapshot["external_imports"].append({"module": module["module"], "path": module["path"], "line": node.lineno, "import": label, "reason": "not_in_production_snapshot"})
            for target in sorted(resolved):
                edges.append({"source": module["module"], "target": target, "source_id": module["id"], "target_id": by_name[target]["id"], "path": module["path"], "line": node.lineno, "kind": "declared_import"})
    snapshot["edges"] = sorted(edges, key=lambda item: (item["source"], item["target"], item["line"]))
    for field in ("external_imports", "dynamic_imports", "parse_errors"):
        snapshot[field].sort(key=lambda item: (item["path"], item["line"] or 0))


def build_snapshot(root: Path | str, ref: str = "HEAD") -> dict:
    root = Path(root).resolve()
    if not ref or ref.startswith("-"):
        raise ValueError("O ref Git deve ser explícito e não pode ser uma opção.")
    commit = _git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").decode("ascii").strip()
    tree = _git(root, "rev-parse", f"{commit}^{{tree}}").decode("ascii").strip()
    snapshot = {"schema_version": "r879.v1", "git": {"requested_ref": ref, "commit": commit, "tree": tree}, "files": [], "modules": [], "edges": [], "external_imports": [], "dynamic_imports": [], "parse_errors": [], "surfaces": [], "configurations": []}
    texts = {}
    for path, mode, kind, oid, data in _blob_records(root, commit):
        classification = classify(path)
        language = LANGUAGES.get(PurePosixPath(path).suffix.lower())
        entry = {"path": path, "git_blob": oid, "git_mode": mode, "git_type": kind, "sha256": hashlib.sha256(data).hexdigest() if data is not None else None, "size": len(data) if data is not None else None, "classification": classification, "language": language}
        snapshot["files"].append(entry)
        if data is None or mode == "120000":
            continue  # Nunca segue symlinks nem submódulos para o filesystem.
        if classification == "production" and language:
            text = data.decode("utf-8-sig", errors="replace")
            package = path.split("/")[0] if "/" in path else "root"
            common = {"id": _node_id(path), "path": path, "sha256": entry["sha256"], "package": package, "layer": LAYERS.get(package, "modulos_adicionais"), "language": language}
            if language == "python":
                common.update({"module": _module_name(path), "kind": "python_module", "parser": "python_ast", "symbols": [], "classes": [], "functions": [], "imports": []})
                snapshot["modules"].append(common)
                texts[path] = text
            else:
                common.update({"kind": "source_surface", "parser": "lexical_declarations", "symbols": _lexical_symbols(text, language)})
                snapshot["surfaces"].append(common)
        if path == "opencode.json":
            try:
                config = json.loads(data)
                safe = {"path": path, "sha256": entry["sha256"]}
                for exported, original in (("agents", "agent"), ("mcp_servers", "mcp"), ("commands", "command")):
                    safe[exported] = sorted(config[original]) if isinstance(config.get(original), dict) else []
                for key in ("default_agent", "model"):
                    safe[key] = config.get(key) if isinstance(config.get(key), str) else None
                snapshot["configurations"].append(safe)
            except (ValueError, TypeError, AttributeError) as exc:
                snapshot["parse_errors"].append({"path": path, "line": None, "message": type(exc).__name__})
    _parse_python(snapshot, texts)
    snapshot["counts"] = {"tracked_files": len(snapshot["files"]), "python_production_modules": len(snapshot["modules"]), "non_python_surfaces": len(snapshot["surfaces"]), "declared_import_edges": len(snapshot["edges"]), "unique_module_pairs": len({(item["source"], item["target"]) for item in snapshot["edges"]}), "classifications": dict(sorted(Counter(item["classification"] for item in snapshot["files"]).items())), "parse_errors": len(snapshot["parse_errors"]), "external_imports": len(snapshot["external_imports"]), "dynamic_imports": len(snapshot["dynamic_imports"])}
    snapshot["limitations"] = ["Snapshot de arquivos versionados no commit indicado; arquivos privados, ignorados e mudanças não commitadas não são lidos.", "Imports AST declarados não comprovam chamadas, execução, prontidão, qualidade ou validação externa.", "Produção é uma classificação por caminho/extensão; o índice preserva todas as demais categorias separadamente.", "Imports externos ou não encontrados não distinguem biblioteca padrão, dependência opcional e import inválido.", "Imports dinâmicos são registrados, sem serem promovidos a arestas executadas.", "Declarações TS/JS/Lean são extração lexical, não parser semântico; podem conter falsos positivos de comentários/strings e omitir formas não suportadas.", "Relações CLI/MCP, gates e fluxos documentados exigem mapas operacionais separados; não são inferidos do grafo AST.", "Submódulos e symlinks permanecem no índice; seus destinos nunca são seguidos.", "Hashes SHA-256 são de blobs locais; não representam assinatura, auditoria externa ou taxa de cobertura."]
    return snapshot


def _quote(value: str) -> str:
    # JSON string é compatível com strings DOT; caracteres de controle escapados.
    return json.dumps(value, ensure_ascii=True)


def _dot(snapshot: dict, overview: bool) -> str:
    lines = ["digraph architecture {", '  graph [overlap=false, splines=false, remincross=false, nslimit=3, nslimit1=1, mclimit=0.1, outputorder=edgesfirst, bgcolor="#f8fafc", fontname="Helvetica", label="Imports declarados no snapshot Git — não rastreamento de execução"];', '  node [shape=box, style="rounded,filled", fillcolor="#e0f2fe", color="#0284c7", fontname="Helvetica", fontsize=9];', '  edge [color="#94a3b8", arrowsize=0.45];']
    if overview:
        packages = Counter(item["package"] for item in snapshot["modules"])
        for package, count in sorted(packages.items()):
            lines.append(f"  {_node_id(package)} [label={_quote(f'{package} ({count} módulos)')}];")
        modules = {item["module"]: item for item in snapshot["modules"]}
        pairs = Counter((modules[item["source"]]["package"], modules[item["target"]]["package"]) for item in snapshot["edges"] if item["source"] in modules and item["target"] in modules)
        for (source, target), count in sorted(pairs.items()):
            if source != target:
                lines.append(f"  {_node_id(source)} -> {_node_id(target)} [label={_quote(str(count))}];")
    else:
        for module in snapshot["modules"]:
            lines.append(f"  {module['id']} [id={_quote(module['id'])}, label={_quote(module['module'])}, tooltip={_quote(module['path'])}];")
        pairs = sorted({(item["source_id"], item["target_id"]) for item in snapshot["edges"]})
        for source, target in pairs:
            lines.append(f"  {source} -> {target};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def write_artifacts(snapshot: dict, outdir: Path | str, *, render: bool = True) -> dict:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    payloads = {"architecture-inventory.json": json.dumps(snapshot, indent=2, ensure_ascii=True, sort_keys=True) + "\n", "overview.dot": _dot(snapshot, True), "dependencies.dot": _dot(snapshot, False)}
    for name, payload in payloads.items():
        (outdir / name).write_text(payload, encoding="utf-8")
    renderers = {}
    if render:
        for stem, engine in (("overview", "dot"), ("dependencies", "sfdp")):
            executable = shutil.which(engine)
            if executable is None:
                raise RuntimeError(f"Graphviz obrigatório para SVG: {engine} não encontrado")
            probe = subprocess.run([executable, "-Tsvg"], input=b"digraph probe {a -> b}", capture_output=True, timeout=10, check=False)
            if probe.returncode and engine == "sfdp":
                engine = "dot"
                executable = shutil.which(engine)
            elif probe.returncode:
                raise RuntimeError(f"Graphviz {engine} não disponibiliza seu layout: {probe.stderr.decode(errors='replace')}")
            subprocess.run([executable, "-Tsvg", str(outdir / f"{stem}.dot"), "-o", str(outdir / f"{stem}.svg")], check=True, timeout=180)
            renderers[stem] = engine
    return {"files": sorted(payloads), "renderers": renderers}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--output", type=Path, default=Path("docs/architecture"))
    parser.add_argument("--check", action="store_true", help="Compara JSON/DOT determinísticos existentes, sem reescrevê-los.")
    args = parser.parse_args(argv)
    snapshot = build_snapshot(args.root, args.ref)
    if args.check:
        expected = {"architecture-inventory.json": json.dumps(snapshot, indent=2, ensure_ascii=True, sort_keys=True) + "\n", "overview.dot": _dot(snapshot, True), "dependencies.dot": _dot(snapshot, False)}
        differences = [name for name, content in expected.items() if not (args.output / name).exists() or (args.output / name).read_text(encoding="utf-8") != content]
        if differences:
            print(json.dumps({"status": "divergent", "files": differences}, ensure_ascii=False))
            return 1
    else:
        write_artifacts(snapshot, args.output)
    print(json.dumps({"git": snapshot["git"], "counts": snapshot["counts"], "status": "matching" if args.check else "generated"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
